"""
Download ZINC15 dataset (100k molecules) for molecule generation training.

This script tries multiple sources to obtain drug-like molecules:
1. ZINC15 API (filtered for drug-like properties)
2. PubChem via RDKit
3. Pre-processed datasets from GitHub/Zenodo
4. Generate synthetic dataset from known drugs
"""

import requests
import pandas as pd
import time
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors
import random


def download_zinc15_api(n_molecules=100000, output_file='data/zinc15_100k.csv'):
    """
    Download molecules from ZINC15 using their API.
    
    ZINC15 API endpoint: https://zinc15.docking.org/substances/subsets/
    We'll use the 'drug-like' subset which is pre-filtered.
    """
    print(f"Attempting to download {n_molecules} molecules from ZINC15 API...")
    
    # ZINC15 drug-like subset parameters
    # Format: smiles only, drug-like properties
    base_url = "https://zinc15.docking.org/substances/subsets/drug-like"
    
    # Try to get SMILES in batch
    params = {
        'count': 'all',
        'page_size': 1000,  # Max per page
    }
    
    molecules = []
    page = 0
    
    try:
        while len(molecules) < n_molecules:
            params['page'] = page
            print(f"  Fetching page {page}... ({len(molecules)} molecules so far)")
            
            response = requests.get(
                f"{base_url}.txt:smiles",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  Error: HTTP {response.status_code}")
                break
            
            # Parse SMILES from response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line and not line.startswith('#'):
                    parts = line.split('\t')
                    if len(parts) >= 1:
                        smiles = parts[0].strip()
                        if Chem.MolFromSmiles(smiles):
                            molecules.append(smiles)
            
            if len(lines) < params['page_size']:
                break  # No more pages
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        if molecules:
            df = pd.DataFrame({'smiles': molecules[:n_molecules]})
            df.to_csv(output_file, index=False)
            print(f"✓ Successfully downloaded {len(df)} molecules from ZINC15")
            return True
            
    except Exception as e:
        print(f"✗ ZINC15 API failed: {e}")
    
    return False


def download_from_guacamol(output_file='data/zinc15_100k.csv'):
    """
    Download GuacaMol training set (subset of ZINC).
    Pre-processed dataset used in benchmarking papers.
    """
    print("Attempting to download GuacaMol dataset...")
    
    urls = [
        "https://figshare.com/ndownloader/files/13612760",  # GuacaMol v1
        "https://raw.githubusercontent.com/BenevolentAI/guacamol/master/guacamol/data/guacamol_v1_train.smiles",
    ]
    
    for url in urls:
        try:
            print(f"  Trying {url}...")
            response = requests.get(url, timeout=60)
            
            if response.status_code == 200:
                # Save and parse
                lines = response.text.strip().split('\n')
                smiles_list = [line.strip() for line in lines if line.strip()]
                
                # Take first 100k
                df = pd.DataFrame({'smiles': smiles_list[:100000]})
                df.to_csv(output_file, index=False)
                print(f"✓ Successfully downloaded {len(df)} molecules from GuacaMol")
                return True
                
        except Exception as e:
            print(f"  Failed: {e}")
            continue
    
    print("✗ GuacaMol download failed")
    return False


def sample_from_pubchem(n_molecules=100000, output_file='data/zinc15_100k.csv'):
    """
    Sample molecules from PubChem using RDKit.
    This is slower but reliable.
    """
    print(f"Attempting to sample {n_molecules} molecules from PubChem...")
    print("Warning: This may take 10-30 minutes...")
    
    try:
        # Use PubChem's FTP for batch download
        # Note: This is a simplified version
        url = "ftp://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/"
        print(f"  PubChem FTP sampling not implemented yet")
        print(f"  This would require downloading large SDF files")
        return False
        
    except Exception as e:
        print(f"✗ PubChem sampling failed: {e}")
        return False


def create_expanded_dataset(input_file='data/zinc15_train.csv', 
                            output_file='data/zinc15_100k.csv',
                            target_size=100000):
    """
    Expand existing small dataset using SMILES enumeration.
    
    For each molecule, generate multiple valid SMILES representations
    (SMILES randomization) to create a larger training set.
    """
    print(f"Expanding existing dataset to {target_size} molecules...")
    
    try:
        # Load existing molecules
        df = pd.read_csv(input_file)
        original_smiles = df['smiles'].tolist()
        print(f"  Loaded {len(original_smiles)} unique molecules")
        
        # Generate multiple SMILES per molecule
        expanded = []
        target_per_mol = target_size // len(original_smiles) + 1
        
        for smiles in original_smiles:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                continue
            
            # Generate randomized SMILES
            for _ in range(target_per_mol):
                random_smiles = Chem.MolToSmiles(mol, doRandom=True)
                expanded.append(random_smiles)
                
                if len(expanded) >= target_size:
                    break
            
            if len(expanded) >= target_size:
                break
        
        # Save expanded dataset
        df_expanded = pd.DataFrame({'smiles': expanded[:target_size]})
        df_expanded.to_csv(output_file, index=False)
        print(f"✓ Successfully expanded to {len(df_expanded)} SMILES representations")
        return True
        
    except Exception as e:
        print(f"✗ Dataset expansion failed: {e}")
        return False


def download_chembl_sample(n_molecules=100000, output_file='data/zinc15_100k.csv'):
    """
    Download sample from ChEMBL database.
    ChEMBL is a manually curated database of bioactive molecules.
    """
    print(f"Attempting to download {n_molecules} molecules from ChEMBL...")
    
    try:
        # ChEMBL web services API
        base_url = "https://www.ebi.ac.uk/chembl/api/data/molecule"
        
        params = {
            'limit': 1000,
            'offset': 0,
            'format': 'json'
        }
        
        molecules = []
        
        while len(molecules) < n_molecules:
            print(f"  Fetching batch... ({len(molecules)} molecules so far)")
            
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code != 200:
                break
            
            data = response.json()
            
            if 'molecules' not in data:
                break
            
            for mol_data in data['molecules']:
                if 'molecule_structures' in mol_data:
                    structures = mol_data['molecule_structures']
                    if structures and 'canonical_smiles' in structures:
                        smiles = structures['canonical_smiles']
                        if smiles and Chem.MolFromSmiles(smiles):
                            molecules.append(smiles)
            
            params['offset'] += params['limit']
            time.sleep(1)  # Rate limiting
            
            if len(data['molecules']) < params['limit']:
                break
        
        if molecules:
            df = pd.DataFrame({'smiles': molecules[:n_molecules]})
            df.to_csv(output_file, index=False)
            print(f"✓ Successfully downloaded {len(df)} molecules from ChEMBL")
            return True
            
    except Exception as e:
        print(f"✗ ChEMBL download failed: {e}")
    
    return False


def main():
    """Try multiple download strategies in order of preference."""
    
    output_file = 'data/zinc15_100k.csv'
    Path('data').mkdir(exist_ok=True)
    
    print("=" * 70)
    print("ZINC15 Dataset Download (100k molecules)")
    print("=" * 70)
    print()
    
    # Strategy 1: ZINC15 API (best quality, drug-like)
    print("Strategy 1: ZINC15 API")
    print("-" * 70)
    if download_zinc15_api(n_molecules=100000, output_file=output_file):
        return validate_and_clean(output_file)
    print()
    
    # Strategy 2: GuacaMol (pre-processed, reliable)
    print("Strategy 2: GuacaMol Pre-processed Dataset")
    print("-" * 70)
    if download_from_guacamol(output_file=output_file):
        return validate_and_clean(output_file)
    print()
    
    # Strategy 3: ChEMBL (bioactive molecules)
    print("Strategy 3: ChEMBL Database")
    print("-" * 70)
    if download_chembl_sample(n_molecules=100000, output_file=output_file):
        return validate_and_clean(output_file)
    print()
    
    # Strategy 4: Expand existing dataset (fallback)
    print("Strategy 4: SMILES Enumeration from Existing Dataset")
    print("-" * 70)
    if create_expanded_dataset(target_size=100000, output_file=output_file):
        return validate_and_clean(output_file)
    print()
    
    print("=" * 70)
    print("✗ All download strategies failed")
    print("Please manually download ZINC15 from https://zinc15.docking.org/")
    print("=" * 70)
    return False


def validate_and_clean(input_file):
    """Validate downloaded molecules and create clean dataset."""
    
    print()
    print("=" * 70)
    print("Validating and cleaning dataset...")
    print("=" * 70)
    
    try:
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} molecules")
        
        # Validate SMILES
        print("Validating SMILES...")
        valid_smiles = []
        for smiles in df['smiles']:
            mol = Chem.MolFromSmiles(smiles)
            if mol is not None:
                # Canonicalize
                canonical = Chem.MolToSmiles(mol)
                valid_smiles.append(canonical)
        
        print(f"Valid SMILES: {len(valid_smiles)} / {len(df)} ({len(valid_smiles)/len(df)*100:.1f}%)")
        
        # Remove duplicates
        df_clean = pd.DataFrame({'smiles': valid_smiles})
        df_clean = df_clean.drop_duplicates(subset='smiles')
        print(f"Unique molecules: {len(df_clean)}")
        
        # Save cleaned dataset
        df_clean.to_csv(input_file, index=False)
        
        # Create train/val split
        print("\nCreating train/validation split (90/10)...")
        df_shuffled = df_clean.sample(frac=1, random_state=42).reset_index(drop=True)
        split_idx = int(len(df_shuffled) * 0.9)
        
        df_train = df_shuffled[:split_idx]
        df_val = df_shuffled[split_idx:]
        
        train_file = input_file.replace('.csv', '_train.csv')
        val_file = input_file.replace('.csv', '_val.csv')
        
        df_train.to_csv(train_file, index=False)
        df_val.to_csv(val_file, index=False)
        
        print(f"Training set: {len(df_train)} molecules → {train_file}")
        print(f"Validation set: {len(df_val)} molecules → {val_file}")
        
        # Calculate statistics
        print("\nDataset Statistics:")
        print("-" * 70)
        
        sample_mols = [Chem.MolFromSmiles(s) for s in df_clean['smiles'].head(1000)]
        sample_mols = [m for m in sample_mols if m is not None]
        
        if sample_mols:
            mw_values = [Descriptors.MolWt(m) for m in sample_mols]
            print(f"Molecular Weight: {min(mw_values):.1f} - {max(mw_values):.1f} Da")
            print(f"Mean MW: {sum(mw_values)/len(mw_values):.1f} Da")
        
        print()
        print("=" * 70)
        print("✓ Dataset preparation complete!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
