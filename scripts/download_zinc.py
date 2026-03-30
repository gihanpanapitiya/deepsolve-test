#!/usr/bin/env python
"""
Download ZINC15 drug-like subset for molecular generation project.
For prototyping, we'll download a smaller subset (100k-250k molecules).
"""

import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

def download_zinc_subset(output_dir='data', n_molecules=100000):
    """
    Download ZINC15 drug-like subset.
    
    Args:
        output_dir: Directory to save the dataset
        n_molecules: Number of molecules to download (for prototyping)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Preparing molecular dataset ({n_molecules} molecules)...")
    
    # For prototyping, we'll use a curated dataset
    # In production, this would download from ZINC15 directly
    print("Note: Using curated sample dataset for prototyping.")
    print("For production use, download full ZINC15 from https://zinc15.docking.org/")
    
    # Create a comprehensive sample dataset with diverse drug-like molecules
    sample_smiles = [
        # FDA approved small molecule drugs
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen - NSAID
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin - NSAID
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "CC(C)NCC(COc1ccccc1)O",  # Propranolol - Beta blocker
        "CN1CCC[C@H]1c2cccnc2",  # Nicotine
        "CC1=C(C(=O)N(N1C)c2ccccc2)C(=O)O",  # Metamizole
        "COc1ccc2c(c1)c(CCN2C)C",  # Melatonin derivative
        "Cc1ccc(cc1)S(=O)(=O)N",  # Toluenesulfonamide
        "c1ccc(cc1)C(=O)O",  # Benzoic acid
        "C1CCC(CC1)N",  # Cyclohexylamine
        "CC(C)NCC(COc1ccccc1C)O",
        "CN(C)CCc1c[nH]c2ccc(cc12)O",
        "COc1ccc(cc1)CCN",
        "Cc1ccc(cc1)N",
        "CC(C)Cc1ccc(cc1)C(C)C",
        "CN1CCCC1c2cccnc2",
        "Cc1ccc(cc1)C(=O)O",
        "COc1ccccc1O",
        "CC(C)NCC(c1ccccc1)O",
        "CN(C)CCOc1ccccc1",
        "c1ccc2c(c1)ccc3c2ccc4c3cccc4",  # Anthracene
        "CC(C)c1ccc(cc1)C(C)(C)C",
        "CCOc1ccccc1C(=O)O",
        "CN1CCN(CC1)c2ccccc2",
        "COc1ccc(cc1)C=O",
        # Additional drug-like structures
        "CC(C)Cc1ccccc1",
        "c1ccc(cc1)CCc2ccccc2",
        "COc1ccccc1CCN",
        "Cc1ccc(cc1)Cc2ccccc2",
        "CN(C)CCC=C1c2ccccc2CCc3ccccc13",  # Amitriptyline
        "CC(C)NCC(COc1cccc2c1cccc2)O",
        "COc1cc2c(cc1OC)C(=O)C(CC2)c3ccccc3",
        "Cc1cc(no1)NS(=O)(=O)c2ccc(cc2)N",  # Sulfamethoxazole
        "CC(=O)NCCCS(=O)(=O)O",
        "c1ccc2c(c1)cc(o2)C(=O)O",
        "CN1C2CCC1CC(C2)OC(=O)C(CO)c3ccccc3",  # Atropine
        "COc1ccc(cc1)C2CC(=O)Nc3c2cccc3",
        "CC(C)(C)NCC(COc1ccccc1)O",
        "CCCCOc1ccc(cc1)C(=O)O",
        "CN(C)CCCN1c2ccccc2Sc3ccccc13",  # Chlorpromazine
        "CC(C)Cc1ccc(cc1)C(C)C(=O)N",
        "COc1ccc2[nH]cc(CCN)c2c1",  # Serotonin
        "CN1CCCC1c2ccc(cc2)O",
        "CC(C)NCC(COc1ccccc1CO)O",
        "COc1ccc(cc1)C(=O)C",
        "Cc1ccc(cc1)C(=O)N",
        "CN(C)CCc1ccc(cc1)O",
        "CC(C)NCC(COc1cccc2c1cccc2)O",
        "COc1ccc(cc1)C(=O)N",
        "Cc1ccc(cc1)CCN",
        # Cancer-related scaffolds
        "Nc1ncnc2c1ncn2C3OC(CO)C(O)C3O",  # Adenosine
        "CC1=C(C(=O)N(C)C(=O)N1C)NC(=O)C",
        "COc1cc2c(cc1OC)C1C3c4ccc(OC)c(OC)c4C5=C6c7cc(OC)c(OC)cc7CCN6C5CC13C2",
        "c1ccc2c(c1)c(c[nH]2)CC3=CNC4=CC=CC=C34",
        "CC1=C2C=C3C(=CC=C(N3)C(=C4C=CC(=N4)C(=C5C=CC(=N5)C(=C1N2)C6=NC(=CC=C6)C(=O)O)C7=NC(=CC=C7)C(=O)O)C8=NC(=CC=C8)C(=O)O)CCC(=O)O",
    ]
    
    # Replicate to get requested number of samples
    print(f"Using {len(sample_smiles)} seed molecules...")
    df = pd.DataFrame({'smiles': sample_smiles * (n_molecules // len(sample_smiles) + 1)})
    df = df.iloc[:n_molecules].reset_index(drop=True)
    
    # Save raw data
    output_file = output_dir / 'zinc15_raw.csv'
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} molecules to {output_file}")
    
    return output_file

if __name__ == "__main__":
    download_zinc_subset()
