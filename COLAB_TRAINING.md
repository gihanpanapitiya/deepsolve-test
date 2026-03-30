# Google Colab Training Instructions

## Quick Start

**1. Open Colab Notebook**

Click this link to open the notebook in Google Colab:
👉 **[Open in Colab]** (upload `transformer_training_colab.ipynb` to Colab)

**2. Enable GPU**
- In Colab: **Runtime** → **Change runtime type** → **GPU** (T4 or better)
- Save settings

**3. Run All Cells**
- **Runtime** → **Run all** (or Shift+Enter through each cell)
- Training will take **4-8 hours** on T4 GPU

**4. Monitor Progress**
- Check training loss, validation loss, and SMILES validity
- Notebook auto-saves checkpoints every 5 epochs
- Best model saved based on validation loss

**5. Download Trained Model**
- Run final cell to download:
  - `best_model.pt` (trained Transformer, ~45 MB)
  - `generated_smiles.csv` (1000 generated SMILES)
  - `training_curves.png` (loss & validity plots)

---

## What the Notebook Does

### Training Pipeline

1. **Setup** (5 minutes)
   - Clones repository from GitHub
   - Installs dependencies (PyTorch, RDKit, transformers)
   - Verifies GPU availability

2. **Data Preparation** (2 minutes)
   - Loads 100k molecules (89,999 train + 10,000 val)
   - Builds character-level vocabulary (~80 characters)
   - Creates PyTorch DataLoaders

3. **Model Architecture**
   - GPT-style Transformer decoder
   - 6 layers, 8 attention heads, 512 embedding dim
   - ~25M parameters (~45 MB model)
   - Causal masking for autoregressive generation

4. **Training** (4-8 hours)
   - 20 epochs with Adam optimizer
   - Cosine annealing learning rate schedule
   - Gradient clipping for stability
   - Validates every epoch

5. **Evaluation**
   - Generates 100 SMILES per epoch
   - Checks validity with RDKit
   - Target: **>90% validity** (vs 85-88% LSTM baseline)

6. **Output**
   - Best model checkpoint
   - 1000 generated SMILES (filtered for validity & uniqueness)
   - Training curves visualization

---

## Expected Results

| Metric | Target | Typical |
|--------|--------|---------|
| **Training Time** | 4-8 hours | 6 hours (T4) |
| **SMILES Validity** | >90% | 90-94% |
| **Final Train Loss** | <0.5 | 0.3-0.5 |
| **Final Val Loss** | <0.6 | 0.4-0.6 |
| **Model Size** | ~45 MB | 45 MB (FP32) |
| **Generated/Hour** | - | ~100 SMILES/s |

---

## Troubleshooting

### GPU Out of Memory

**Symptoms**: `RuntimeError: CUDA out of memory`

**Solutions**:
1. Reduce batch size in cell "Create PyTorch Dataset":
   ```python
   BATCH_SIZE = 64  # or 32 if still failing
   ```

2. Reduce model size in cell "Define Transformer Model":
   ```python
   model = SMILESTransformer(
       vocab_size=VOCAB_SIZE,
       d_model=256,  # reduced from 512
       nhead=8,
       num_layers=4,  # reduced from 6
       ...
   )
   ```

### Low SMILES Validity (<80%)

**Symptoms**: Generated SMILES mostly invalid

**Solutions**:
1. Train for more epochs:
   ```python
   NUM_EPOCHS = 30  # increased from 20
   ```

2. Adjust generation temperature in "Generate Samples":
   ```python
   samples = generate_samples(model, device, temperature=0.6)  # lower = more conservative
   ```

3. Increase model capacity (if GPU memory allows)

### Training Loss Not Decreasing

**Symptoms**: Loss plateaus or increases

**Solutions**:
1. Check learning rate:
   ```python
   optimizer = optim.Adam(model.parameters(), lr=5e-5)  # reduced from 1e-4
   ```

2. Add warmup scheduler:
   ```python
   from transformers import get_linear_schedule_with_warmup
   scheduler = get_linear_schedule_with_warmup(
       optimizer,
       num_warmup_steps=500,
       num_training_steps=len(train_loader) * NUM_EPOCHS
   )
   ```

### Colab Session Disconnected

**Symptoms**: Training interrupted, lost progress

**Solutions**:
1. **Prevent disconnection**:
   - Keep Colab tab active
   - Use browser extension to prevent sleep
   - Consider Colab Pro for longer sessions (24h vs 12h)

2. **Resume from checkpoint**:
   ```python
   checkpoint = torch.load('checkpoint_epoch_10.pt')
   model.load_state_dict(checkpoint['model_state_dict'])
   optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
   start_epoch = checkpoint['epoch'] + 1
   ```

### No GPU Available

**Symptoms**: Device shows `cpu` instead of `cuda`

**Solutions**:
1. Enable GPU: **Runtime** → **Change runtime type** → **GPU**
2. Check GPU quota (free tier has limits)
3. Consider Colab Pro for guaranteed GPU access

---

## Cost Estimates

### Google Colab

| Tier | GPU | Cost | Training Time |
|------|-----|------|---------------|
| **Free** | T4 (sporadic) | $0 | 6-8 hours |
| **Colab Pro** | T4/V100 | $10/month | 4-6 hours |
| **Colab Pro+** | V100/A100 | $50/month | 2-4 hours |

**Recommendation**: Start with **free tier**. Upgrade if you need:
- Guaranteed GPU access
- Longer sessions (24h vs 12h)
- Faster GPUs (V100/A100)

### Alternatives

| Platform | GPU | Cost | Notes |
|----------|-----|------|-------|
| **Paperspace Gradient** | P5000 | ~$0.51/hour (~$3-4 total) | Free tier available |
| **AWS SageMaker** | ml.g4dn.xlarge | ~$0.74/hour (~$5-6 total) | Complex setup |
| **Lambda Labs** | A10 | ~$0.60/hour (~$3-5 total) | Simple, cost-effective |

---

## After Training: Next Steps

Once training completes:

1. **Download Files**:
   - `best_model.pt` → Upload to GitHub repo (`models/` folder)
   - `generated_smiles.csv` → For initial analysis
   - `training_curves.png` → Add to report

2. **Phase 3.3**: Implement Reinforcement Learning
   - Fine-tune model with solubility constraints
   - Use `src/property_calculator.py` for reward function
   - Target: logS > 1, MW < 300, cancer drug properties

3. **Phase 4**: Generate & Analyze
   - Generate 10k-100k candidate molecules
   - Filter by constraints
   - Analyze novelty & diversity
   - Select top 100 for review

---

## Tips for Successful Training

✅ **DO**:
- Keep Colab tab open and active
- Monitor first few epochs to catch errors early
- Save checkpoints frequently (auto-saved every 5 epochs)
- Check SMILES validity trends (should increase over epochs)

❌ **DON'T**:
- Close Colab tab (will disconnect)
- Run on CPU (too slow, impractical)
- Skip validation checks (need to verify learning)
- Forget to download model before session ends

---

## Questions?

Check:
1. **PHASE2_REPORT.md** - Phase 2 completion summary
2. **PLAN.md** - Full project plan
3. **README.md** - Project overview
4. **GitHub Issues** - Ask questions

---

**Status**: Ready for training! 🚀  
**Estimated completion**: 4-8 hours after starting  
**Next phase**: RL fine-tuning with constraints
