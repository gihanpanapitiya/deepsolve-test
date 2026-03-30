#!/usr/bin/env python
"""
Clean and validate SMILES data.
- Remove invalid SMILES
- Remove duplicates
- Calculate statistics
- Create train/val split
"""

import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit import RDLogger
from tqdm import tqdm
import numpy as np

# Suppress RDKit warnings
RDLogger.DisableLog('rdApp.*')

def validate_smiles(smiles):
    """Check if SMILES can be parsed by RDKit."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except:
        return False

def canonicalize_smiles(smiles):
    """Canonicalize SMILES string."""
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            return Chem.MolToSmiles(mol, canonical=True)
    except:
        pass
    return None

def clean_and_validate(input_file='data/zinc15_raw.csv', 
                      output_dir='data',
                      train_split=0.9,
                      random_seed=42):
    """
    Clean and validate SMILES data.
    
    Args:
        input_file: Path to raw SMILES data
        output_dir: Directory to save cleaned data
        train_split: Fraction of data for training
        random_seed: Random seed for reproducibility
    """
    print(f"Loading SMILES from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} molecules")
    
    # Get SMILES column
    if 'smiles' in df.columns:
        smiles_col = 'smiles'
    elif 'SMILES' in df.columns:
        smiles_col = 'SMILES'
    else:
        smiles_col = df.columns[0]
    
    print(f"\nValidating SMILES...")
    valid_smiles = []
    invalid_count = 0
    
    for smi in tqdm(df[smiles_col]):
        if isinstance(smi, str) and validate_smiles(smi):
            valid_smiles.append(smi)
        else:
            invalid_count += 1
    
    print(f"Valid SMILES: {len(valid_smiles)}")
    print(f"Invalid SMILES: {invalid_count}")
    
    # Canonicalize SMILES
    print(f"\nCanonicalizing SMILES...")
    canonical_smiles = []
    for smi in tqdm(valid_smiles):
        canon = canonicalize_smiles(smi)
        if canon:
            canonical_smiles.append(canon)
    
    print(f"Canonicalized: {len(canonical_smiles)}")
    
    # Remove duplicates
    print(f"\nRemoving duplicates...")
    df_clean = pd.DataFrame({'smiles': canonical_smiles})
    df_clean = df_clean.drop_duplicates(subset=['smiles'])
    print(f"Unique molecules: {len(df_clean)}")
    
    # Calculate statistics
    print(f"\n=== Dataset Statistics ===")
    print(f"Total molecules: {len(df)}")
    print(f"Valid molecules: {len(valid_smiles)}")
    print(f"Unique molecules: {len(df_clean)}")
    print(f"Duplicates removed: {len(canonical_smiles) - len(df_clean)}")
    print(f"Invalid/failed: {invalid_count}")
    
    # Calculate SMILES length statistics
    smiles_lengths = df_clean['smiles'].str.len()
    print(f"\nSMILES length statistics:")
    print(f"  Mean: {smiles_lengths.mean():.2f}")
    print(f"  Median: {smiles_lengths.median():.2f}")
    print(f"  Min: {smiles_lengths.min()}")
    print(f"  Max: {smiles_lengths.max()}")
    print(f"  Std: {smiles_lengths.std():.2f}")
    
    # Create train/val split
    print(f"\n Creating train/validation split ({train_split:.0%}/{1-train_split:.0%})...")
    df_shuffled = df_clean.sample(frac=1, random_state=random_seed).reset_index(drop=True)
    
    split_idx = int(len(df_shuffled) * train_split)
    df_train = df_shuffled.iloc[:split_idx]
    df_val = df_shuffled.iloc[split_idx:]
    
    print(f"Training set: {len(df_train)} molecules")
    print(f"Validation set: {len(df_val)} molecules")
    
    # Save to files
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    train_file = output_dir / 'zinc15_train.csv'
    val_file = output_dir / 'zinc15_val.csv'
    
    df_train.to_csv(train_file, index=False)
    df_val.to_csv(val_file, index=False)
    
    print(f"\nSaved training data to {train_file}")
    print(f"Saved validation data to {val_file}")
    
    return df_train, df_val

if __name__ == "__main__":
    clean_and_validate()
