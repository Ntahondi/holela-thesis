"""
Visual Concrete Defect Dataset Loader
Streams real concrete surface imagery from:
1. S2DS Dataset (743 high-res images with pixel-level defect masks).
2. Concrete Structures with Multi-Feature Backgrounds (2,750 annotated images).
Maps defects into a 4-class structural condition hierarchy:
  0: Intact Substrate (Normal)
  1: Crack Fissure (Minor to Moderate)
  2: Spalling / Damage Cavity (Moderate to Severe)
  3: Corrosion / Efflorescence (Chemical / Rebar Degradation)
Fulfills PhD Chapter 5, Section 5.7.1 & Section 5.8.
"""

import os
import zipfile
import io
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from typing import Tuple, Dict, Any, List, Optional

class ConcreteVisionDataset(Dataset):
    """PyTorch Dataset for real concrete surface defect images."""
    def __init__(self, image_records: List[Dict[str, Any]], transform=None):
        """
        image_records: List of dicts with {'zip_path': str, 'img_name': str, 'label': int}
        """
        self.records = image_records
        self.transform = transform
        self._zip_handles = {}

    def _get_zip(self, zip_path: str) -> zipfile.ZipFile:
        if zip_path not in self._zip_handles:
            self._zip_handles[zip_path] = zipfile.ZipFile(zip_path, 'r')
        return self._zip_handles[zip_path]

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        rec = self.records[idx]
        z = self._get_zip(rec['zip_path'])
        img_bytes = z.read(rec['img_name'])
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')

        if self.transform:
            img = self.transform(img)

        return img, rec['label']


class ConcreteVisionPipeline:
    """Orchestrates ingestion, labeling, and train/val/test splits for real image datasets."""

    CLASS_NAMES = {
        0: "Intact Substrate",
        1: "Structural Crack",
        2: "Concrete Spalling / Damage",
        3: "Corrosion / Efflorescence"
    }

    def __init__(
        self,
        s2ds_zip: str = 'ai_models/data/raw/public/s2ds.zip',
        damage_zip: str = 'ai_models/data/raw/public/Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds.zip'
    ):
        self.s2ds_zip = s2ds_zip
        self.damage_zip = damage_zip

    def index_s2ds_dataset(self) -> List[Dict[str, Any]]:
        """Indexes image-mask pairs from S2DS and determines primary defect label."""
        records = []
        if not os.path.exists(self.s2ds_zip):
            return records

        with zipfile.ZipFile(self.s2ds_zip, 'r') as z:
            img_names = [n for n in z.namelist() if n.endswith('.png') and not n.endswith('_lab.png') and any(split in n for split in ['train/', 'val/', 'test/'])]

            for name in img_names:
                mask_name = name.replace('.png', '_lab.png')
                try:
                    mask_bytes = z.read(mask_name)
                    mask = np.array(Image.open(io.BytesIO(mask_bytes)))
                    # Detect presence of classes via color thresholds
                    has_crack = np.any((mask[:, :, 0] > 200) & (mask[:, :, 1] < 50) & (mask[:, :, 2] < 50))
                    has_spalling = np.any((mask[:, :, 0] < 50) & (mask[:, :, 1] > 200) & (mask[:, :, 2] < 50))
                    has_corrosion = np.any((mask[:, :, 0] < 50) & (mask[:, :, 1] < 50) & (mask[:, :, 2] > 200))
                    has_efflor = np.any((mask[:, :, 0] > 200) & (mask[:, :, 1] > 200) & (mask[:, :, 2] < 50))

                    if has_spalling:
                        label = 2  # Spalling / Cavity
                    elif has_corrosion or has_efflor:
                        label = 3  # Chemical / Rebar corrosion
                    elif has_crack:
                        label = 1  # Crack
                    else:
                        label = 0  # Intact Substrate

                    records.append({
                        'zip_path': self.s2ds_zip,
                        'img_name': name,
                        'label': label,
                        'split': name.split('/')[0]
                    })
                except Exception:
                    continue
        return records

    def index_damage_detection_dataset(self, max_samples: int = 1500) -> List[Dict[str, Any]]:
        """Indexes images and XML annotations from Multi-Feature Background dataset."""
        records = []
        if not os.path.exists(self.damage_zip):
            return records

        with zipfile.ZipFile(self.damage_zip, 'r') as z:
            xml_names = [n for n in z.namelist() if n.startswith('2750/annot/') and n.endswith('.xml')][:max_samples]

            for x_name in xml_names:
                try:
                    xml_bytes = z.read(x_name)
                    root = ET.fromstring(xml_bytes)
                    obj_names = [obj.findtext('name', '').lower() for obj in root.findall('object')]

                    if 'damage' in obj_names:
                        label = 2  # Spalling / Cavity
                    elif 'crack' in obj_names:
                        label = 1  # Crack
                    else:
                        label = 0

                    img_name = x_name.replace('annot/', 'img/').replace('.xml', '.png')
                    records.append({
                        'zip_path': self.damage_zip,
                        'img_name': img_name,
                        'label': label,
                        'split': 'train'
                    })
                except Exception:
                    continue
        return records

    def build_dataloaders(
        self,
        batch_size: int = 32,
        img_size: int = 224,
        num_workers: int = 0
    ) -> Dict[str, DataLoader]:
        """Builds train, val, and test DataLoaders with tropical field augmentations."""
        from sklearn.model_selection import train_test_split

        s2ds_recs = self.index_s2ds_dataset()
        damage_recs = self.index_damage_detection_dataset(max_samples=1500)
        all_records = s2ds_recs + damage_recs

        labels = [r['label'] for r in all_records]
        train_recs, temp_recs = train_test_split(all_records, test_size=0.30, random_state=42, stratify=labels)
        temp_labels = [r['label'] for r in temp_recs]
        val_recs, test_recs = train_test_split(temp_recs, test_size=0.50, random_state=42, stratify=temp_labels)

        # Tropical Field Augmentations (harsh sun, shadows, camera motion)
        train_transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.2),
            transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.15),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        eval_transform = transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        train_ds = ConcreteVisionDataset(train_recs, transform=train_transform)
        val_ds = ConcreteVisionDataset(val_recs, transform=eval_transform)
        test_ds = ConcreteVisionDataset(test_recs, transform=eval_transform)

        return {
            'train': DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers),
            'val': DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
            'test': DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
            'meta': {
                'total_samples': len(all_records),
                'train_samples': len(train_recs),
                'val_samples': len(val_recs),
                'test_samples': len(test_recs)
            }
        }
