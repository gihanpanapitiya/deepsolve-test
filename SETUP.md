# Setup Guide - DeepSolve Molecular Generation

This guide documents the installation and setup process for the DeepSolve molecular generation project.

---

## Environment Information

- **Python Version:** 3.12
- **Platform:** macOS / Linux / Windows
- **Package Manager:** pip / conda

---

## Installation Steps

### 1. Prerequisites

Ensure you have Python 3.10+ and pip installed:

```bash
python --version  # Should be 3.10 or higher
pip --version
```

### 2. Create Virtual Environment (Recommended)

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n deepsolve python=3.12
conda activate deepsolve
```

### 3. Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Verify PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# Verify RDKit
python -c "import rdkit; print(f'RDKit: {rdkit.__version__}')"

# Verify other key packages
python -c "import pandas, numpy, matplotlib; print('Core packages OK')"
```

### 5. Test Molecular Property Calculator

```bash
# Run property calculator tests
python src/property_calculator.py

# Run unit tests
python -m unittest tests.test_property_calculator -v
```

---

## Installed Packages

### Core Dependencies
- `torch>=2.0.0` - PyTorch for deep learning (✅ 2.8.0 installed)
- `numpy>=1.24.0` - Numerical computing
- `pandas>=2.0.0` - Data manipulation
- `scikit-learn>=1.3.0` - Machine learning utilities

### Cheminformatics
- `rdkit>=2023.3.1` - Chemical informatics toolkit (✅ 2023.9.1 installed)
- ~~`mordred>=1.2.0`~~ - Additional molecular descriptors (⚠️ installation issues)

### Machine Learning
- `transformers>=4.30.0` - Transformer models
- ~~`deepchem>=2.7.0`~~ - Deep learning for chemistry (⚠️ Python 3.12 incompatible)

### Utilities
- `matplotlib>=3.7.0` - Plotting
- `seaborn>=0.12.0` - Statistical visualization
- `tqdm>=4.65.0` - Progress bars
- `jupyter>=1.0.0` - Jupyter notebooks
- `datasets>=2.12.0` - Dataset management
- `requests>=2.31.0` - HTTP library

---

## Known Issues and Solutions

### Issue 1: DeepChem Installation (Python 3.12)

**Problem:** DeepChem is not compatible with Python 3.12

**Solution Options:**
1. Skip DeepChem (current approach - RDKit provides all needed functionality)
2. Downgrade to Python 3.10 or 3.11:
   ```bash
   conda create -n deepsolve python=3.10
   conda activate deepsolve
   pip install -r requirements.txt
   ```

**Impact:** Low - RDKit provides all required molecular property calculations

### Issue 2: Mordred Installation

**Problem:** Mordred has installation issues with current environment

**Solution:** Skip Mordred installation
```bash
# Install requirements excluding mordred
pip install torch numpy pandas scikit-learn rdkit transformers \
    matplotlib seaborn tqdm jupyter datasets requests
```

**Impact:** Low - RDKit descriptors are sufficient

### Issue 3: No GPU Available

**Problem:** CUDA GPU not detected, running on CPU

**Check GPU availability:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
```

**Solution for GPU support:**
1. Install CUDA toolkit from NVIDIA
2. Install PyTorch with CUDA support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

**Impact:** Medium - Training will be slower on CPU, but functional

### Issue 4: RDKit Import Warnings

**Problem:** RDKit may show warnings about missing features

**Solution:** Suppress warnings in code:
```python
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')
```

---

## Directory Structure

After setup, your directory should look like:

```
deepsolve-test/
├── data/                    # Dataset files
├── src/                     # Source code
│   └── property_calculator.py
├── scripts/                 # Utility scripts
│   ├── download_zinc.py
│   └── clean_and_validate.py
├── tests/                   # Unit tests
│   └── test_property_calculator.py
├── notebooks/               # Jupyter notebooks
│   └── 01_data_preparation.ipynb
├── results/                 # Output files
│   └── figures/
├── requirements.txt         # Python dependencies
├── PHASE1_REPORT.md        # Phase 1 report
└── SETUP.md                # This file
```

---

## Quick Start

After installation, run these commands to verify everything works:

```bash
# 1. Download dataset (creates prototype dataset)
python scripts/download_zinc.py

# 2. Clean and validate SMILES
python scripts/clean_and_validate.py

# 3. Run unit tests
python -m unittest tests.test_property_calculator -v

# 4. Test property calculator
python src/property_calculator.py

# 5. Start Jupyter notebook (optional)
jupyter notebook notebooks/01_data_preparation.ipynb
```

Expected output:
- Dataset: 100,000 molecules → 53 unique after deduplication
- Train/val split: 47/6 molecules
- All tests passing: 9/9 ✅

---

## Hardware Requirements

### Minimum Requirements
- **CPU:** Dual-core processor
- **RAM:** 4 GB
- **Storage:** 2 GB free space
- **OS:** Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)

### Recommended for Training (Phase 2)
- **CPU:** 8+ cores
- **RAM:** 16 GB+
- **GPU:** NVIDIA GPU with 8+ GB VRAM (e.g., RTX 3070, A100)
- **Storage:** 50 GB+ free space (for full ZINC15 dataset)

---

## Troubleshooting

### Python Package Conflicts

If you encounter package version conflicts:

```bash
# Create fresh environment
pip freeze > old_requirements.txt
pip uninstall -y -r old_requirements.txt
pip install -r requirements.txt
```

### Jupyter Kernel Issues

If Jupyter doesn't detect your virtual environment:

```bash
# Install ipykernel
pip install ipykernel

# Add kernel
python -m ipykernel install --user --name=deepsolve --display-name="DeepSolve"

# Select kernel in Jupyter: Kernel > Change kernel > DeepSolve
```

### RDKit Installation on Windows

If RDKit installation fails on Windows:

```bash
# Use conda instead
conda install -c conda-forge rdkit
```

### Memory Issues with Large Datasets

If you run out of memory processing large datasets:

```python
# Process in batches
import pandas as pd

# Read in chunks
chunk_size = 10000
for chunk in pd.read_csv('data.csv', chunksize=chunk_size):
    # Process chunk
    pass
```

---

## Environment Variables (Optional)

For production use, consider setting these environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc

# Suppress RDKit warnings
export RDKIT_NOWARN=1

# PyTorch thread control
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# CUDA device selection (if multiple GPUs)
export CUDA_VISIBLE_DEVICES=0
```

---

## Next Steps

After completing setup:

1. ✅ Verify all tests pass
2. ✅ Run data preparation notebook
3. ✅ Review PHASE1_REPORT.md
4. 🚀 Proceed to Phase 2: Model Development

---

## Support

For issues or questions:
- Check PHASE1_REPORT.md for known issues
- Review test outputs for error messages
- Verify package versions match requirements.txt

---

**Last Updated:** Phase 1 Completion  
**Environment:** Python 3.12, PyTorch 2.8.0, RDKit 2023.9.1
