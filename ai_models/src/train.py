"""
Master Training and Comparative Benchmarking Orchestrator
Executes training for:
1. Primary 1D-CNN Model
2. Baseline LSTM Recurrent Model
3. Baseline Support Vector Machine (SVM)
4. Baseline Random Forest (RF)
Produces all empirical figures and tables mandated in PhD Chapter 5 (5.8 & 5.9).
"""

import os
import sys
import time
import copy
import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import ReduceLROnPlateau

# Local imports
from data_loader import SHMDataPipeline
from preprocessor import SHMPreprocessor
from models.cnn_1d import ConcreteSHMCNN1D
from models.lstm_baseline import ConcreteSHMLSTM
from models.classical_baselines import SVMBaseline, RandomForestBaseline
from evaluate import SHMModelEvaluator
from noise_simulator import FieldNoiseSimulator
from idss_decision_logic import IDSSDecisionEngine

def train_pytorch_model(
    model: nn.Module,
    dataloaders: dict,
    device: str = 'cpu',
    num_epochs: int = 35,
    learning_rate: float = 1e-3,
    patience: int = 7,
    weights_path: str = "ai_models/weights/best_model.pth"
):
    """
    Standardized training loop with validation early stopping and learning rate scheduling.
    """
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    best_loss = float('inf')
    best_model_weights = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0

    history = {
        'train_loss': [], 'val_loss': [],
        'train_acc': [], 'val_acc': []
    }

    print(f"\n--- Starting Training: {model.__class__.__name__} on {device} ---")
    start_time = time.time()

    for epoch in range(1, num_epochs + 1):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for X_batch, y_batch in dataloaders['train']:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * X_batch.size(0)
            preds = torch.argmax(outputs, dim=-1)
            correct += (preds == y_batch).sum().item()
            total += y_batch.size(0)

        epoch_train_loss = running_loss / total
        epoch_train_acc = correct / total

        # Validation Phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for X_batch, y_batch in dataloaders['val']:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)

                val_loss += loss.item() * X_batch.size(0)
                preds = torch.argmax(outputs, dim=-1)
                val_correct += (preds == y_batch).sum().item()
                val_total += y_batch.size(0)

        epoch_val_loss = val_loss / val_total
        epoch_val_acc = val_correct / val_total
        scheduler.step(epoch_val_loss)

        history['train_loss'].append(epoch_train_loss)
        history['val_loss'].append(epoch_val_loss)
        history['train_acc'].append(epoch_train_acc)
        history['val_acc'].append(epoch_val_acc)

        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:02d}/{num_epochs:02d} | Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.3f} | Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.3f}")

        # Early Stopping Check
        if epoch_val_loss < best_loss:
            best_loss = epoch_val_loss
            best_model_weights = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            os.makedirs(os.path.dirname(weights_path), exist_ok=True)
            torch.save(best_model_weights, weights_path)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered at epoch {epoch}. Best Val Loss: {best_loss:.4f}")
                break

    elapsed = time.time() - start_time
    print(f"Training completed in {elapsed:.1f} seconds. Best weights saved to {weights_path}")
    model.load_state_dict(best_model_weights)
    return model, history


def main():
    print("=========================================================================")
    print("SMMS AI & DEEP LEARNING MODEL SUITE (PhD Thesis Chapter 5 Execution)")
    print("Candidate: Paul Zablon Holela | Supervisor: Prof. John Makunza, UDSM")
    print("=========================================================================")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Hardware Compute Device: {device.upper()}")

    # 1. Dataset Generation & Preprocessing (Sections 5.7 & 5.8)
    print("\n[Step 1/6] Ingesting and Preprocessing SHM Telemetry...")
    X_raw, y_raw = SHMDataPipeline.generate_calibrated_concrete_dataset(
        num_windows=2400, window_size=256, num_channels=4, random_seed=42
    )

    preprocessor = SHMPreprocessor(sampling_rate=100.0, filter_low=0.5, filter_high=40.0)
    X_filtered = preprocessor.butter_bandpass_filter(X_raw)

    # 70% Train, 15% Validation, 15% Test Split (Section 3.5.6)
    X_train, y_train, X_val, y_val, X_test, y_test = SHMDataPipeline.train_val_test_split(
        X_filtered, y_raw, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15, random_state=42
    )

    # Fit normalizer on training set only (prevent data leakage)
    preprocessor.fit_normalizer(X_train)
    X_train_norm = preprocessor.transform_normalizer(X_train)
    X_val_norm = preprocessor.transform_normalizer(X_val)
    X_test_norm = preprocessor.transform_normalizer(X_test)

    dataloaders = SHMDataPipeline.get_dataloaders(
        X_train_norm, y_train, X_val_norm, y_val, X_test_norm, y_test, batch_size=32
    )

    evaluator = SHMModelEvaluator()
    benchmark_metrics = {}

    # 2. Train Primary Model: 1D-CNN (Section 5.8)
    print("\n[Step 2/6] Training Primary Model: ConcreteSHMCNN1D...")
    cnn_model = ConcreteSHMCNN1D(in_channels=4, num_classes=4, base_filters=32, dropout_rate=0.3)
    cnn_weights = "ai_models/weights/cnn_1d_best.pth"
    cnn_model, cnn_history = train_pytorch_model(
        cnn_model, dataloaders, device=device, num_epochs=35, learning_rate=1e-3, patience=7, weights_path=cnn_weights
    )

    # Evaluate 1D-CNN
    cnn_model.eval()
    with torch.no_grad():
        test_logits = cnn_model(torch.tensor(X_test_norm).to(device))
        cnn_probs = torch.softmax(test_logits, dim=-1).cpu().numpy()
        cnn_preds = np.argmax(cnn_probs, axis=-1)

    cnn_eval = evaluator.calculate_metrics(y_test, cnn_preds, cnn_probs)
    benchmark_metrics["1D-CNN (Proposed)"] = cnn_eval
    print(f"1D-CNN Performance: Accuracy={cnn_eval['accuracy']:.4f}, F1-Score={cnn_eval['f1_weighted']:.4f}, AUC-ROC={cnn_eval.get('roc_auc_macro', 0.0):.4f}")

    # Generate Figures for 1D-CNN
    evaluator.plot_training_history(cnn_history, model_name="CNN_1D")
    evaluator.plot_confusion_matrix(y_test, cnn_preds, model_name="CNN_1D")
    evaluator.plot_roc_curves(y_test, cnn_probs, model_name="CNN_1D")

    # 3. Train Baseline 1: LSTM Recurrent Model (Section 5.9.4)
    print("\n[Step 3/6] Training Benchmark 1: ConcreteSHMLSTM...")
    lstm_model = ConcreteSHMLSTM(in_channels=4, hidden_dim=64, num_layers=2, num_classes=4, dropout_rate=0.3)
    lstm_weights = "ai_models/weights/lstm_best.pth"
    lstm_model, _ = train_pytorch_model(
        lstm_model, dataloaders, device=device, num_epochs=30, learning_rate=1e-3, patience=6, weights_path=lstm_weights
    )

    lstm_model.eval()
    with torch.no_grad():
        lstm_logits = lstm_model(torch.tensor(X_test_norm).to(device))
        lstm_probs = torch.softmax(lstm_logits, dim=-1).cpu().numpy()
        lstm_preds = np.argmax(lstm_probs, axis=-1)

    lstm_eval = evaluator.calculate_metrics(y_test, lstm_preds, lstm_probs)
    benchmark_metrics["LSTM Baseline"] = lstm_eval
    print(f"LSTM Performance: Accuracy={lstm_eval['accuracy']:.4f}, F1-Score={lstm_eval['f1_weighted']:.4f}")

    # 4. Feature Extraction & Classical Baselines: SVM & Random Forest (Section 5.9.4)
    print("\n[Step 4/6] Extracting Statistical Features for SVM & Random Forest...")
    X_train_feats = preprocessor.extract_statistical_features(X_train_norm)
    X_test_feats = preprocessor.extract_statistical_features(X_test_norm)

    # SVM
    print("Training Support Vector Machine (SVM RBF)...")
    svm = SVMBaseline(C=1.5, kernel='rbf', probability=True)
    svm.fit(X_train_feats, y_train)
    svm_preds = svm.predict(X_test_feats)
    svm_probs = svm.predict_proba(X_test_feats)
    svm_eval = evaluator.calculate_metrics(y_test, svm_preds, svm_probs)
    benchmark_metrics["SVM (RBF Kernel)"] = svm_eval
    svm.save("ai_models/weights/svm_baseline.joblib")
    print(f"SVM Performance: Accuracy={svm_eval['accuracy']:.4f}, F1-Score={svm_eval['f1_weighted']:.4f}")

    # Random Forest
    print("Training Random Forest Classifier...")
    rf = RandomForestBaseline(n_estimators=100, max_depth=12)
    rf.fit(X_train_feats, y_train)
    rf_preds = rf.predict(X_test_feats)
    rf_probs = rf.predict_proba(X_test_feats)
    rf_eval = evaluator.calculate_metrics(y_test, rf_preds, rf_probs)
    benchmark_metrics["Random Forest"] = rf_eval
    rf.save("ai_models/weights/rf_baseline.joblib")
    print(f"Random Forest Performance: Accuracy={rf_eval['accuracy']:.4f}, F1-Score={rf_eval['f1_weighted']:.4f}")

    # Export Benchmark Table
    csv_path, tex_path = evaluator.export_benchmark_comparison(benchmark_metrics)
    print(f"\nBenchmark comparison exported to:\n  - CSV: {csv_path}\n  - LaTeX: {tex_path}")

    # 5. Noise & Packet Drop Robustness Simulation (Section 5.9.5)
    print("\n[Step 5/6] Testing Robustness under Real-World Tropical Noise & Packet Loss...")
    noise_results = FieldNoiseSimulator.evaluate_model_under_noise_sweep(
        cnn_model, X_test_norm, y_test,
        snr_levels=[30.0, 20.0, 15.0, 10.0, 5.0],
        packet_drop_rates=[0.0, 0.05, 0.10, 0.15, 0.20, 0.25],
        device=device
    )
    evaluator.plot_noise_degradation(noise_results, model_name="CNN_1D")
    print("Noise degradation curves generated and saved to reports/figures/noise_degradation_cnn_1d.png")

    # 6. IDSS Decision Chain Demonstration (Section 5.10.3)
    print("\n[Step 6/6] Demonstrating Sensor-to-Action Decision Chain (IDSS Engine)...")
    sample_idx = 0
    sample_pred = int(cnn_preds[sample_idx])
    sample_probs = cnn_probs[sample_idx].tolist()
    asset_meta = {
        "asset_id": "TANROADS-DSM-BR-014",
        "asset_name": "Tanzanite Bridge - Pier 4 Expansion Span",
        "road_class": "Trunk",
        "importance_weight": 1.4
    }
    decision_output = IDSSDecisionEngine.process_telemetry_to_decision(
        predicted_class=sample_pred,
        class_probabilities=sample_probs,
        telemetry_summary={"peak_strain": 310.5, "rms_vibration": 2.85, "crack_opening_mm": 0.95},
        asset_metadata=asset_meta
    )
    print(f"Sample Asset: {decision_output['asset_name']}")
    print(f"Predicted Condition: {SHMDataPipeline.CONDITION_CLASSES[sample_pred]} (Confidence: {decision_output['condition_state']['confidence']}%)")
    print(f"Priority Index Score: {decision_output['decision_chain']['priority_index_score']}/100")
    print(f"Recommended Action: {decision_output['decision_chain']['recommended_action']}")
    print(f"Resource Allocation: {decision_output['decision_chain']['resource_allocation']}")
    print(f"Urgency Window: {decision_output['decision_chain']['maximum_response_window_days']} days")

    print("\n=========================================================================")
    print("PHASE 1 COMPLETE: All AI Models, Baselines, and Thesis Deliverables Ready!")
    print("=========================================================================")

if __name__ == "__main__":
    main()
