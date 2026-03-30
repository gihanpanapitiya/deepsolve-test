"""
Test script to find and verify available solubility prediction models.
"""

print("Testing available solubility prediction models...")
print("=" * 60)

# Test 1: Try ChemBERTa models from Hugging Face
print("\n1. Testing ChemBERTa models:")
try:
    from transformers import AutoTokenizer, AutoModel
    
    # Try common ChemBERTa model names
    model_candidates = [
        "seyonec/ChemBERTa-zinc-base-v1",
        "DeepChem/ChemBERTa-77M-MLM",
        "DeepChem/ChemBERTa-77M-MTR",
        "chem-lab/chemberta-solubility",  # From research
    ]
    
    for model_name in model_candidates:
        try:
            print(f"  Trying {model_name}...", end=" ")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            print("✓ Available")
        except Exception as e:
            print(f"✗ Not found ({type(e).__name__})")
            
except ImportError:
    print("  ✗ Transformers not installed")

# Test 2: Check if we can use RDKit-based solubility estimates
print("\n2. Testing RDKit-based approaches:")
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen
    
    # Test ESOL formula (simple linear model)
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    mol = Chem.MolFromSmiles(test_smiles)
    
    if mol:
        # ESOL: log S = 0.16 - 0.63·cLogP - 0.0062·MW + 0.066·RB - 0.74·AP
        logp = Crippen.MolLogP(mol)
        mw = Descriptors.MolWt(mol)
        rb = Descriptors.NumRotatableBonds(mol)
        ap = Descriptors.NumAromaticRings(mol)
        
        esol_logs = 0.16 - 0.63 * logp - 0.0062 * mw + 0.066 * rb - 0.74 * ap
        
        print(f"  ✓ ESOL formula working")
        print(f"    Test (aspirin): logS = {esol_logs:.2f}")
        print(f"    (Experimental logS for aspirin: ~-1.19)")
        
except ImportError:
    print("  ✗ RDKit not available")

# Test 3: Check for solubility-trained models on Hugging Face Hub
print("\n3. Searching Hugging Face for solubility models:")
try:
    from huggingface_hub import list_models
    
    print("  Searching for 'solubility' models...")
    models = list(list_models(search="solubility", limit=5))
    
    if models:
        print(f"  Found {len(models)} models:")
        for model in models:
            print(f"    - {model.modelId}")
    else:
        print("  No models found with 'solubility' tag")
        
except ImportError:
    print("  ✗ huggingface_hub not installed (pip install huggingface_hub)")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("Recommendation: Use ESOL formula as baseline (fast, no download)")
print("For better accuracy, fine-tune ChemBERTa on AqSolDB dataset")
