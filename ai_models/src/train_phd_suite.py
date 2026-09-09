"""
Master Doctoral Research Training Suite
Integrates:
- Engine 1: Physics-Aware Bridge Telemetry (1D-CNN, Bi-LSTM, SVM, Random Forest with Focal Loss & Monte Carlo Dropout)
- Engine 2: Real Concrete Visual Inspection (2D-CNN with Grad-CAM XAI)
- Robustness Testing: Tropical Noise & Cellular Packet Dropout (Section 5.9.5)
- Intelligent Decision Support System (IDSS) Sensor-to-Action Decision Logic (Section 5.10.3)
Generates complete empirical figures, tables, and weights for PhD Thesis Chapter 5.
"""

import os
import sys
import time
import copy
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

# Ensure local modules directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Local modules
from data_loader_telemetry import BridgeTelemetryPipeline, TelemetryWindowDataset
from data_loader_vision import ConcreteVisionPipeline
from preprocessor import SHMPreprocessor
from losses import MultiClassFocalLoss
from models.cnn_1d import ConcreteSHMCNN1D
from models.cnn_2d import ConcreteDamageCNN2D
from models.lstm_baseline import ConcreteSHMLSTM
from models.classical_baselines import SVMBaseline, RandomForestBaseline
from evaluate import SHMModelEvaluator
from noise_simulator import FieldNoiseSimulator
from explainability import ConcreteGradCAM
from idss_decision_logic import IDSSDecisionEngine

def train_nn_model(
    model: nn.Module,
    dataloaders: dict,
    loss_fn: nn.Module,
    device: str = 'cpu',
    num_epochs: int = 25,
    learning_rate: float = 1e-3,
    patience: int = 5,
    weights_path: str = "ai_models/weights/model.pth"
):
    model.to(device)
    optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

    best_loss = float('inf')
    best_weights = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

    print(f"\nTraining {model.__class__.__name__} on {device} (Max Epochs: {num_epochs})...")
    start_time = time.time()

    for epoch in range(1, num_epochs + 1):
        # Training
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for X_batch, y_batch in dataloaders['train']:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = loss_fn(outputs, y_batch)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * X_batch.size(0)
            preds = torch.argmax(outputs, dim=-1)
            correct += (preds == y_batch).sum().item()
            total += y_batch.size(0)

        tr_loss = running_loss / total
        tr_acc = correct / total

        # Validation
        model.eval()
        val_loss, v_correct, v_total = 0.0, 0, 0
        with torch.no_grad():
            for X_batch, y_batch in dataloaders['val']:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = loss_fn(outputs, y_batch)
                val_loss += loss.item() * X_batch.size(0)
                preds = torch.argmax(outputs, dim=-1)
                v_correct += (preds == y_batch).sum().item()
                v_total += y_batch.size(0)

        v_loss = val_loss / v_total
        v_acc = v_correct / v_total
        scheduler.step(v_loss)

        history['train_loss'].append(tr_loss)
        history['val_loss'].append(v_loss)
        history['train_acc'].append(tr_acc)
        history['val_acc'].append(v_acc)

        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:02d}/{num_epochs:02d} | Train Loss: {tr_loss:.4f} Acc: {tr_acc:.3f} | Val Loss: {v_loss:.4f} Acc: {v_acc:.3f}")

        if v_loss < best_loss:
            best_loss = v_loss
            best_weights = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            os.makedirs(os.path.dirname(weights_path), exist_ok=True)
            torch.save(best_weights, weights_path)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping at epoch {epoch}. Best Val Loss: {best_loss:.4f}")
                break

    print(f"Finished in {time.time() - start_time:.1f}s. Saved: {weights_path}")
    model.load_state_dict(best_weights)
    return model, history


def main():
    print("=========================================================================")
    print("DOCTORAL AI MODEL SUITE FOR CONCRETE INFRASTRUCTURE SMMS")
    print("PhD Candidate: Paul Zablon Holela | Supervisor: Prof. John Makunza, UDSM")
    print("=========================================================================")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Compute Device: {device.upper()}")

    evaluator = SHMModelEvaluator()
    benchmark_metrics = {}

    # =========================================================================
    # PART 1: ENGINE 1 - CONTINUOUS BRIDGE TELEMETRY (1D-CNN, LSTM, SVM, RF)
    # =========================================================================
    print("\n" + "="*50)
    print("PART 1: ENGINE 1 - CONTINUOUS BRIDGE TELEMETRY (43,200 Timestamps)")
    print("="*50)

    telemetry_pipeline = BridgeTelemetryPipeline('ai_models/data/raw/public/archive.zip')
    X_win, y_alert, y_state = telemetry_pipeline.generate_sliding_windows(window_size=128, stride=32)
    print(f"Total operational sequence windows: {X_win.shape[0]} ({X_win.shape[1]} timesteps x {X_win.shape[2]} channels)")

    # Stratified 70/15/15 Split
    X_train, y_train, X_val, y_val, X_test, y_test = BridgeTelemetryPipeline.train_val_test_split(
        X_win, y_state, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42
    )

    # Z-Score Normalization
    preprocessor = SHMPreprocessor(sampling_rate=1.0 / 60.0) # 1-minute sampling
    preprocessor.fit_normalizer(X_train)
    X_train_norm = preprocessor.transform_normalizer(X_train)
    X_val_norm = preprocessor.transform_normalizer(X_val)
    X_test_norm = preprocessor.transform_normalizer(X_test)

    # DataLoaders
    train_loader = torch.utils.data.DataLoader(TelemetryWindowDataset(X_train_norm, y_train), batch_size=32, shuffle=True)
    val_loader = torch.utils.data.DataLoader(TelemetryWindowDataset(X_val_norm, y_val), batch_size=32, shuffle=False)
    test_loader = torch.utils.data.DataLoader(TelemetryWindowDataset(X_test_norm, y_test), batch_size=32, shuffle=False)
    telemetry_loaders = {'train': train_loader, 'val': val_loader, 'test': test_loader}

    # Class distribution weighting for Focal Loss
    class_counts = np.bincount(y_train, minlength=4)
    total_samples = len(y_train)
    class_weights = torch.tensor(total_samples / (4.0 * np.maximum(class_counts, 1)), dtype=torch.float32)
    focal_loss_fn = MultiClassFocalLoss(alpha=class_weights, gamma=2.0)

    # 1.1 Train Proposed Model: Physics-Aware 1D-CNN
    print("\n--- Training Proposed 1D-CNN (with Focal Loss) ---")
    cnn_1d = ConcreteSHMCNN1D(in_channels=8, num_classes=4, base_filters=32, dropout_rate=0.3)
    cnn_1d_path = "ai_models/weights/cnn_1d_telemetry_best.pth"
    cnn_1d, cnn_1d_hist = train_nn_model(
        cnn_1d, telemetry_loaders, focal_loss_fn, device=device, num_epochs=25, learning_rate=1e-3, patience=5, weights_path=cnn_1d_path
    )

    # Evaluate 1D-CNN
    cnn_1d.eval()
    with torch.no_grad():
        test_logits = cnn_1d(torch.tensor(X_test_norm).to(device))
        cnn_probs = torch.softmax(test_logits, dim=-1).cpu().numpy()
        cnn_preds = np.argmax(cnn_probs, axis=-1)

    eval_cnn1d = evaluator.calculate_metrics(y_test, cnn_preds, cnn_probs)
    benchmark_metrics["Proposed 1D-CNN (Telemetry)"] = eval_cnn1d
    print(f"1D-CNN: Accuracy={eval_cnn1d['accuracy']:.4f}, Weighted F1={eval_cnn1d['f1_weighted']:.4f}, Macro ROC-AUC={eval_cnn1d.get('roc_auc_macro', 0.0):.4f}")

    evaluator.plot_training_history(cnn_1d_hist, model_name="Telemetry_1D_CNN")
    evaluator.plot_confusion_matrix(y_test, cnn_preds, model_name="Telemetry_1D_CNN")
    evaluator.plot_roc_curves(y_test, cnn_probs, model_name="Telemetry_1D_CNN")

    # 1.2 Uncertainty Quantification via Monte Carlo Dropout
    print("\nEvaluating Epistemic Uncertainty via Monte Carlo Dropout (Section 5.8.5)...")
    sample_tensor = torch.tensor(X_test_norm[:5]).to(device)
    mc_mean, mc_std = cnn_1d.predict_with_uncertainty(sample_tensor, num_samples=30)
    print(f"Sample test prediction confidence bounds (Mean +/- 2*Std):")
    for i in range(len(sample_tensor)):
        pred_c = torch.argmax(mc_mean[i]).item()
        c_mean = mc_mean[i, pred_c].item() * 100
        c_std = mc_std[i, pred_c].item() * 100
        print(f"  Asset Window {i+1}: Class {pred_c} ({c_mean:.1f}% ± {2*c_std:.2f}% 95% CI)")

    # 1.3 Train Benchmark 1: Bi-LSTM
    print("\n--- Training Benchmark 1: Bi-LSTM ---")
    lstm = ConcreteSHMLSTM(in_channels=8, hidden_dim=64, num_layers=2, num_classes=4, dropout_rate=0.3)
    lstm_path = "ai_models/weights/lstm_telemetry_best.pth"
    lstm, _ = train_nn_model(
        lstm, telemetry_loaders, focal_loss_fn, device=device, num_epochs=20, learning_rate=1e-3, patience=5, weights_path=lstm_path
    )
    lstm.eval()
    with torch.no_grad():
        lstm_logits = lstm(torch.tensor(X_test_norm).to(device))
        lstm_probs = torch.softmax(lstm_logits, dim=-1).cpu().numpy()
        lstm_preds = np.argmax(lstm_probs, axis=-1)

    eval_lstm = evaluator.calculate_metrics(y_test, lstm_preds, lstm_probs)
    benchmark_metrics["Bi-LSTM Benchmark"] = eval_lstm
    print(f"Bi-LSTM: Accuracy={eval_lstm['accuracy']:.4f}, Weighted F1={eval_lstm['f1_weighted']:.4f}")

    # 1.4 Feature Extraction & Classical Benchmarks (SVM & Random Forest)
    print("\n--- Training Classical Baselines: SVM & Random Forest ---")
    X_train_feats = preprocessor.extract_statistical_features(X_train_norm)
    X_test_feats = preprocessor.extract_statistical_features(X_test_norm)

    svm = SVMBaseline(C=2.0, kernel='rbf', probability=True)
    svm.fit(X_train_feats, y_train)
    svm_preds = svm.predict(X_test_feats)
    svm_probs = svm.predict_proba(X_test_feats)
    eval_svm = evaluator.calculate_metrics(y_test, svm_preds, svm_probs)
    benchmark_metrics["SVM (RBF Kernel)"] = eval_svm
    svm.save("ai_models/weights/svm_telemetry.joblib")
    print(f"SVM: Accuracy={eval_svm['accuracy']:.4f}, Weighted F1={eval_svm['f1_weighted']:.4f}")

    rf = RandomForestBaseline(n_estimators=100, max_depth=12)
    rf.fit(X_train_feats, y_train)
    rf_preds = rf.predict(X_test_feats)
    rf_probs = rf.predict_proba(X_test_feats)
    eval_rf = evaluator.calculate_metrics(y_test, rf_preds, rf_probs)
    benchmark_metrics["Random Forest (100 Trees)"] = eval_rf
    rf.save("ai_models/weights/rf_telemetry.joblib")
    print(f"Random Forest: Accuracy={eval_rf['accuracy']:.4f}, Weighted F1={eval_rf['f1_weighted']:.4f}")

    # Export Benchmark Table to CSV and LaTeX
    csv_tab, tex_tab = evaluator.export_benchmark_comparison(benchmark_metrics)
    print(f"Exported benchmark tables:\n  - CSV: {csv_tab}\n  - LaTeX: {tex_tab}")

    # 1.5 Field Noise & Network Packet-Loss Testing (Section 5.9.5)
    print("\n--- Testing Field Noise & Cellular Dropouts (Section 5.9.5) ---")
    noise_results = FieldNoiseSimulator.evaluate_model_under_noise_sweep(
        cnn_1d, X_test_norm, y_test,
        snr_levels=[30.0, 20.0, 15.0, 10.0, 5.0],
        packet_drop_rates=[0.0, 0.05, 0.10, 0.15, 0.20, 0.25],
        device=device
    )
    evaluator.plot_noise_degradation(noise_results, model_name="Telemetry_1D_CNN")
    print("Saved noise degradation plot: reports/figures/noise_degradation_telemetry_1d_cnn.png")

    # =========================================================================
    # PART 2: ENGINE 2 - VISUAL CONCRETE DEFECT INSPECTION (2D-CNN & GRAD-CAM)
    # =========================================================================
    print("\n" + "="*50)
    print("PART 2: ENGINE 2 - VISUAL CONCRETE DEFECT INSPECTION (S2DS + Background)")
    print("="*50)

    vision_pipeline = ConcreteVisionPipeline()
    vision_loaders = vision_pipeline.build_dataloaders(batch_size=16, img_size=224)
    print(f"Visual dataset indexed: {vision_loaders['meta']['total_samples']} images "
          f"({vision_loaders['meta']['train_samples']} train, {vision_loaders['meta']['val_samples']} val, {vision_loaders['meta']['test_samples']} test)")

    cnn_2d = ConcreteDamageCNN2D(in_channels=3, num_classes=4, base_channels=32, dropout_rate=0.3)
    cnn_2d_path = "ai_models/weights/cnn_2d_visual_best.pth"
    ce_loss_fn = nn.CrossEntropyLoss()
    cnn_2d, _ = train_nn_model(
        cnn_2d, vision_loaders, ce_loss_fn, device=device, num_epochs=12, learning_rate=5e-4, patience=3, weights_path=cnn_2d_path
    )

    # Grad-CAM Explainability Demonstration
    print("\nGenerating Explainable AI (Grad-CAM) Visual Heatmap (Section 5.8)...")
    gradcam = ConcreteGradCAM(cnn_2d)
    
    # Grab a test image
    for test_imgs, test_lbls in vision_loaders['test']:
        sample_img_t = test_imgs[0:1].to(device)
        sample_lbl = test_lbls[0].item()
        break

    with torch.no_grad():
        v_probs = cnn_2d.predict_probabilities(sample_img_t).cpu().numpy()[0]
        v_pred = int(np.argmax(v_probs))

    cam_map = gradcam.generate_heatmap(sample_img_t, target_class=v_pred)
    
    # Denormalize image for plotting
    raw_img = sample_img_t[0].permute(1, 2, 0).cpu().numpy()
    raw_img = (raw_img * np.array([0.229, 0.224, 0.225])) + np.array([0.485, 0.456, 0.406])
    raw_img = np.clip(raw_img, 0.0, 1.0)

    overlay_img = gradcam.overlay_heatmap_on_image(raw_img, cam_map)
    gradcam_fig_path = "ai_models/reports/figures/gradcam_visual_defect_explanation.png"
    gradcam.save_gradcam_figure(
        raw_img, cam_map, overlay_img,
        predicted_class_name=ConcreteVisionPipeline.CLASS_NAMES[v_pred],
        confidence_pct=v_probs[v_pred] * 100,
        output_path=gradcam_fig_path
    )
    print(f"Saved Grad-CAM explainability figure: {gradcam_fig_path}")

    # =========================================================================
    # PART 3: IDSS SENSOR-TO-ACTION DECISION CHAIN (Section 5.10.3)
    # =========================================================================
    print("\n" + "="*50)
    print("PART 3: SENSOR-TO-ACTION DECISION CHAIN (IDSS Engine - Section 5.10.3)")
    print("="*50)

    sample_decision = IDSSDecisionEngine.process_telemetry_to_decision(
        predicted_class=int(cnn_preds[0]),
        class_probabilities=cnn_probs[0].tolist(),
        telemetry_summary={
            "max_strain": float(X_test[0, :, 0].max()),
            "max_vibration": float(X_test[0, :, 1].max()),
            "crack_propagation_mm": float(X_test[0, :, 2].max())
        },
        asset_metadata={
            "asset_id": "TZ-TANROADS-BR-004",
            "asset_name": "Tanzanite Bridge - Expansion Pier Segment",
            "road_class": "Trunk",
            "importance_weight": 1.5
        }
    )
    print(f"Asset: {sample_decision['asset_name']} ({sample_decision['asset_id']})")
    print(f"Assessed Condition: Class {sample_decision['condition_state']['class_index']} (Confidence: {sample_decision['condition_state']['confidence']}%)")
    print(f"Severity Level: {sample_decision['decision_chain']['severity_level']}")
    print(f"Recommended Action: {sample_decision['decision_chain']['recommended_action']}")
    print(f"Priority Index (MPI): {sample_decision['decision_chain']['priority_index_score']}/100")
    print(f"Resource Tier: {sample_decision['decision_chain']['resource_allocation']}")
    print(f"Mandatory Action Window: {sample_decision['decision_chain']['maximum_response_window_days']} days")

    print("\n=========================================================================")
    print("DOCTORAL MODEL SUITE EXECUTION COMPLETE: All Figures, Tables & Weights Saved!")
    print("=========================================================================")

if __name__ == "__main__":
    main()
