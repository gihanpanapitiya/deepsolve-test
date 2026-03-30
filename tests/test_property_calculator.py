"""
Unit tests for molecular property calculator.
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from property_calculator import (
    validate_smiles,
    calculate_all_properties,
    check_cancer_drug_constraints,
    lipinski_rule_of_five
)


class TestPropertyCalculator(unittest.TestCase):
    """Test molecular property calculations."""
    
    def setUp(self):
        """Set up test molecules."""
        self.valid_smiles = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"  # Ibuprofen
        self.invalid_smiles = "INVALID_SMILES_123"
        
    def test_validate_smiles_valid(self):
        """Test SMILES validation with valid SMILES."""
        self.assertTrue(validate_smiles(self.valid_smiles))
    
    def test_validate_smiles_invalid(self):
        """Test SMILES validation with invalid SMILES."""
        self.assertFalse(validate_smiles(self.invalid_smiles))
    
    def test_calculate_all_properties_valid(self):
        """Test property calculation with valid SMILES."""
        props = calculate_all_properties(self.valid_smiles)
        self.assertIsNotNone(props)
        self.assertIn('molecular_weight', props)
        self.assertIn('logp', props)
        self.assertIn('logS', props)  # Solubility
        self.assertIn('hbd', props)
        self.assertIn('hba', props)
        self.assertIn('psa', props)
        self.assertIn('aromatic_rings', props)
        self.assertIn('rotatable_bonds', props)
        self.assertIn('sa_score', props)
        self.assertIn('qed', props)
    
    def test_calculate_all_properties_invalid(self):
        """Test property calculation with invalid SMILES."""
        props = calculate_all_properties(self.invalid_smiles)
        self.assertIsNone(props)
    
    def test_check_cancer_drug_constraints(self):
        """Test cancer drug constraint checking."""
        passes, constraints, properties = check_cancer_drug_constraints(self.valid_smiles)
        self.assertIsInstance(passes, bool)
        self.assertIsInstance(constraints, dict)
        self.assertIsInstance(properties, dict)
        self.assertIn('solubility_check', constraints)  # NEW: solubility constraint
        self.assertIn('mw_check', constraints)
        self.assertIn('logp_check', constraints)
        self.assertIn('hbd_check', constraints)
        self.assertIn('hba_check', constraints)
        self.assertIn('psa_check', constraints)
        self.assertIn('rotatable_bonds_check', constraints)
    
    def test_lipinski_rule_of_five(self):
        """Test Lipinski's Rule of Five checking."""
        passes, rules, properties = lipinski_rule_of_five(self.valid_smiles)
        self.assertIsInstance(passes, bool)
        self.assertIsInstance(rules, dict)
        self.assertIsInstance(properties, dict)
        self.assertIn('mw_rule', rules)
        self.assertIn('logp_rule', rules)
        self.assertIn('hbd_rule', rules)
        self.assertIn('hba_rule', rules)
    
    def test_property_ranges(self):
        """Test that calculated properties are in reasonable ranges."""
        props = calculate_all_properties(self.valid_smiles)
        self.assertGreater(props['molecular_weight'], 0)
        self.assertIsNotNone(props['logS'])  # Solubility should be calculated
        self.assertGreater(props['qed'], 0)
        self.assertLessEqual(props['qed'], 1)
        self.assertGreaterEqual(props['hbd'], 0)
        self.assertGreaterEqual(props['hba'], 0)
        self.assertGreaterEqual(props['psa'], 0)
        self.assertGreaterEqual(props['aromatic_rings'], 0)
        self.assertGreaterEqual(props['rotatable_bonds'], 0)
        self.assertGreaterEqual(props['sa_score'], 1)
        self.assertLessEqual(props['sa_score'], 10)
    
    def test_solubility_calculation(self):
        """Test ESOL solubility calculation."""
        # Test with highly soluble molecule (glycine: NCC(=O)O)
        glycine_smiles = "NCC(=O)O"
        props = calculate_all_properties(glycine_smiles)
        self.assertIsNotNone(props['logS'])
        # Glycine is highly soluble, logS should be positive
        self.assertGreater(props['logS'], -2)  # Reasonable for small polar molecule
        
        # Test with lipophilic molecule (ibuprofen)
        props_ibupro = calculate_all_properties(self.valid_smiles)
        # Lipophilic drugs typically have negative logS
        self.assertLess(props_ibupro['logS'], 0)


class TestSpecificMolecules(unittest.TestCase):
    """Test specific drug molecules."""
    
    def test_aspirin(self):
        """Test aspirin properties."""
        smiles = "CC(=O)Oc1ccccc1C(=O)O"
        props = calculate_all_properties(smiles)
        self.assertIsNotNone(props)
        self.assertAlmostEqual(props['molecular_weight'], 180.16, places=1)
        self.assertEqual(props['hbd'], 1)
        self.assertEqual(props['hba'], 3)
    
    def test_caffeine(self):
        """Test caffeine properties."""
        smiles = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
        props = calculate_all_properties(smiles)
        self.assertIsNotNone(props)
        self.assertAlmostEqual(props['molecular_weight'], 194.19, places=1)
        self.assertEqual(props['hbd'], 0)
        self.assertEqual(props['hba'], 3)


if __name__ == '__main__':
    unittest.main()
