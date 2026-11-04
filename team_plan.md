# DeepSolve Team Plan

## Project North Star
Develop a computational pipeline that generates novel, synthetically accessible drug candidate molecules (SMILES) with aqueous solubility > 1 logS, MW < 300 Da, and cancer-drug-specific property constraints — and deliver a ranked library of top candidates for human review.

---

## Completed Milestones

### Phase 1: Environment & Data Foundation ✅
- Environment setup (PyTorch 2.8.0, RDKit 2023.9.1)
- ZINC15 dataset downloaded (100k raw → 53 unique molecules)
- Molecular property calculator (`src/property_calculator.py`), 9/9 tests passing
- Data preparation notebook (`notebooks/01_data_preparation.ipynb`)

### Phase 2: Solubility Prediction ✅
- ESOL-based solubility predictor implemented and integrated
- 10/10 unit tests passing; benchmarked on known drugs
- Deliverable: `src/property_calculator.py` (extended), `tests/test_property_calculator.py`

### Phase 3.1: Transformer Training Notebook ✅
- GPT-style Transformer (6 layers, 8 heads, 512d) Colab notebook created
- Deliverable: `notebooks/transformer_training_colab.ipynb`, `COLAB_TRAINING.md`
- **Next action**: @gihanpanapitiya to run training on Colab T4 GPU (4–8 hrs)

---

## Current Milestone: Complete Generative Model (Phase 3)

### Task 3.2 — Reinforcement Learning Fine-tuning
- **Owner**: TBD (assign once Colab training completes)
- **Description**: PPO/REINFORCE fine-tuning with reward = solubility (0.4) + MW (0.2) + cancer constraints (0.2) + SA (0.1) + novelty (0.1)
- **Dependencies**: Task 3.1 trained model checkpoint
- **Deliverable**: `src/rl_trainer.py`, `models/smiles_generator_finetuned.pt`
- **Status**: ⏳ Blocked on 3.1 training run

### Task 3.3 — Validity & Constraint Filters
- **Owner**: TBD
- **Description**: SMILES syntax validation, property constraint checking, duplicate removal
- **Dependencies**: Task 3.2
- **Deliverable**: `src/molecule_filter.py`
- **Status**: ⏳ TODO

---

## Next Milestone: Generation & Evaluation (Phase 4)

### Task 4.1 — Generate Candidate Molecules
- **Owner**: TBD
- **Description**: Generate 10k–100k candidate SMILES; apply constraint filters; rank by composite score
- **Dependencies**: Task 3.3
- **Deliverable**: `results/generated_molecules.csv`
- **Status**: ⏸ TODO

### Task 4.2 — Analysis & Visualization
- **Owner**: TBD
- **Description**: Property distributions, novelty/diversity analysis, visualize top candidates
- **Dependencies**: Task 4.1
- **Deliverable**: `notebooks/analysis.ipynb`, `results/figures/`
- **Status**: ⏸ TODO

### Task 4.3 — Top Candidate Selection for Human Review
- **Owner**: @gihanpanapitiya
- **Description**: Select top 100 molecules by composite score; produce property table
- **Dependencies**: Task 4.2
- **Deliverable**: `results/top_candidates.csv` + report
- **Status**: ⏸ TODO

---

## Future: Refinement & Iteration (Phase 5)
- Incorporate human feedback on candidate selection
- Adjust reward weights; optional re-training
- Final large-scale generation (100k+ molecules)
- Full documentation and code release

---

## Key Risks
1. **Small training set** (53 unique molecules): may limit model diversity → monitor generation diversity; consider ChEMBL supplement
2. **MW < 300 Da** is restrictive → monitor hit rate; may relax to < 350 Da
3. **Solubility predictor accuracy**: ESOL is approximate → ensemble or experimental validation for final candidates
4. **Synthetic feasibility**: enforce SA score ≤ 3.0 in reward function

---

*Last updated: 2026-11-04 (heartbeat reconciliation — initial plan)*
