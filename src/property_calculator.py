"""
Molecular Property Calculator

Functions to calculate molecular properties and validate drug-likeness.
Uses RDKit for all calculations.
"""

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, QED, Crippen
from rdkit.Chem import rdMolDescriptors
from rdkit import RDLogger
from typing import Dict, Optional, Tuple
import numpy as np

# Suppress RDKit warnings
RDLogger.DisableLog('rdApp.*')


def validate_smiles(smiles: str) -> bool:
    """
    Validate if a SMILES string can be parsed by RDKit.
    
    Args:
        smiles: SMILES string
    
    Returns:
        True if valid, False otherwise
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol is not None
    except:
        return False


def calculate_molecular_weight(mol: Chem.Mol) -> float:
    """Calculate molecular weight in Daltons."""
    return Descriptors.MolWt(mol)


def calculate_logp(mol: Chem.Mol) -> float:
    """Calculate LogP (lipophilicity) using Crippen method."""
    return Crippen.MolLogP(mol)


def calculate_hbd(mol: Chem.Mol) -> int:
    """Calculate number of hydrogen bond donors."""
    return Lipinski.NumHDonors(mol)


def calculate_hba(mol: Chem.Mol) -> int:
    """Calculate number of hydrogen bond acceptors."""
    return Lipinski.NumHAcceptors(mol)


def calculate_psa(mol: Chem.Mol) -> float:
    """Calculate polar surface area (PSA) in Ų."""
    return Descriptors.TPSA(mol)


def calculate_aromatic_rings(mol: Chem.Mol) -> int:
    """Calculate number of aromatic rings."""
    return Descriptors.NumAromaticRings(mol)


def calculate_rotatable_bonds(mol: Chem.Mol) -> int:
    """Calculate number of rotatable bonds."""
    return Lipinski.NumRotatableBonds(mol)


def calculate_sa_score(mol: Chem.Mol) -> float:
    """
    Calculate synthetic accessibility score (1-10).
    Lower scores indicate easier synthesis.
    
    Note: This is a simplified version. For production use,
    consider using the full SA_Score implementation.
    """
    # Simple approximation based on complexity
    # Real SA score requires additional data files
    try:
        # Use fragment-based complexity as proxy
        num_atoms = mol.GetNumAtoms()
        num_rings = Descriptors.RingCount(mol)
        num_heteroatoms = Lipinski.NumHeteroatoms(mol)
        num_rotatable = Lipinski.NumRotatableBonds(mol)
        
        # Simple heuristic (not the real SA score algorithm)
        complexity = (
            num_atoms * 0.05 + 
            num_rings * 0.5 + 
            num_heteroatoms * 0.1 +
            num_rotatable * 0.3
        )
        
        # Map to 1-10 scale (lower is better)
        sa_score = min(10, max(1, complexity / 2))
        return sa_score
    except:
        return 5.0  # Default neutral score


def calculate_qed(mol: Chem.Mol) -> float:
    """
    Calculate QED (Quantitative Estimate of Drug-likeness).
    Range: 0-1, higher is more drug-like.
    """
    try:
        return QED.qed(mol)
    except:
        return 0.0


def calculate_all_properties(smiles: str) -> Optional[Dict[str, float]]:
    """
    Calculate all molecular properties for a SMILES string.
    
    Args:
        smiles: SMILES string
    
    Returns:
        Dictionary of properties or None if invalid SMILES
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    properties = {
        'smiles': smiles,
        'molecular_weight': calculate_molecular_weight(mol),
        'logp': calculate_logp(mol),
        'hbd': calculate_hbd(mol),
        'hba': calculate_hba(mol),
        'psa': calculate_psa(mol),
        'aromatic_rings': calculate_aromatic_rings(mol),
        'rotatable_bonds': calculate_rotatable_bonds(mol),
        'sa_score': calculate_sa_score(mol),
        'qed': calculate_qed(mol),
    }
    
    return properties


def check_cancer_drug_constraints(
    smiles: str,
    mw_max: float = 300.0,
    logp_min: float = 1.5,
    logp_max: float = 4.0,
    hbd_max: int = 5,
    hba_max: int = 10,
    psa_max: float = 140.0,
    rotatable_bonds_max: int = 10
) -> Tuple[bool, Dict[str, bool], Dict[str, float]]:
    """
    Check if a molecule meets cancer drug constraints.
    
    Constraints (based on cancer drug fragment specifications):
    - MW < 300 Da
    - LogP between 1.5-4.0
    - HBD ≤ 5
    - HBA ≤ 10
    - PSA < 140 Ų
    - Rotatable bonds ≤ 10
    
    Args:
        smiles: SMILES string
        mw_max: Maximum molecular weight (Da)
        logp_min: Minimum LogP
        logp_max: Maximum LogP
        hbd_max: Maximum hydrogen bond donors
        hba_max: Maximum hydrogen bond acceptors
        psa_max: Maximum polar surface area (Ų)
        rotatable_bonds_max: Maximum rotatable bonds
    
    Returns:
        Tuple of:
        - Overall pass/fail (bool)
        - Dictionary of individual constraint checks (bool)
        - Dictionary of calculated properties (float)
    """
    properties = calculate_all_properties(smiles)
    
    if properties is None:
        return False, {}, {}
    
    constraints = {
        'mw_check': properties['molecular_weight'] < mw_max,
        'logp_check': logp_min <= properties['logp'] <= logp_max,
        'hbd_check': properties['hbd'] <= hbd_max,
        'hba_check': properties['hba'] <= hba_max,
        'psa_check': properties['psa'] < psa_max,
        'rotatable_bonds_check': properties['rotatable_bonds'] <= rotatable_bonds_max,
    }
    
    overall_pass = all(constraints.values())
    
    return overall_pass, constraints, properties


def lipinski_rule_of_five(smiles: str) -> Tuple[bool, Dict[str, bool], Dict[str, float]]:
    """
    Check if a molecule passes Lipinski's Rule of Five.
    
    Rules:
    - Molecular weight ≤ 500 Da
    - LogP ≤ 5
    - Hydrogen bond donors ≤ 5
    - Hydrogen bond acceptors ≤ 10
    
    Args:
        smiles: SMILES string
    
    Returns:
        Tuple of:
        - Overall pass/fail (bool)
        - Dictionary of individual rule checks (bool)
        - Dictionary of calculated properties (float)
    """
    properties = calculate_all_properties(smiles)
    
    if properties is None:
        return False, {}, {}
    
    rules = {
        'mw_rule': properties['molecular_weight'] <= 500,
        'logp_rule': properties['logp'] <= 5,
        'hbd_rule': properties['hbd'] <= 5,
        'hba_rule': properties['hba'] <= 10,
    }
    
    overall_pass = all(rules.values())
    
    return overall_pass, rules, properties


if __name__ == "__main__":
    # Test the functions
    test_smiles = [
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
    ]
    
    print("Testing molecular property calculator...")
    print("=" * 60)
    
    for smi in test_smiles:
        print(f"\nSMILES: {smi}")
        
        props = calculate_all_properties(smi)
        if props:
            print(f"  MW: {props['molecular_weight']:.2f} Da")
            print(f"  LogP: {props['logp']:.2f}")
            print(f"  HBD: {props['hbd']}")
            print(f"  HBA: {props['hba']}")
            print(f"  PSA: {props['psa']:.2f} Ų")
            print(f"  Aromatic rings: {props['aromatic_rings']}")
            print(f"  Rotatable bonds: {props['rotatable_bonds']}")
            print(f"  SA Score: {props['sa_score']:.2f}")
            print(f"  QED: {props['qed']:.3f}")
        
        # Check cancer drug constraints
        passes, constraints, _ = check_cancer_drug_constraints(smi)
        print(f"  Cancer drug constraints: {'PASS' if passes else 'FAIL'}")
        if not passes:
            failed = [k for k, v in constraints.items() if not v]
            print(f"    Failed: {', '.join(failed)}")
        
        # Check Lipinski's Rule of Five
        passes_ro5, rules, _ = lipinski_rule_of_five(smi)
        print(f"  Lipinski's Rule of Five: {'PASS' if passes_ro5 else 'FAIL'}")
        if not passes_ro5:
            failed_ro5 = [k for k, v in rules.items() if not v]
            print(f"    Failed: {', '.join(failed_ro5)}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
