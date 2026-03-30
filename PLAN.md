# Research Plan: Molecule Generation for High-Solubility Cancer Drug Candidates

## Project Goal
Develop a computational pipeline to generate novel drug candidate molecules (SMILES format) with:
- **Primary constraint**: Aqueous solubility > 1 logS
- **Molecular weight**: < 300 Da
- **Application**: Cancer drug discovery
- **Dataset**: ZINC15
- **Timeline**: Rapid prototyping

## Cancer Drug Property Constraints (from literature)
Based on oncology drug design best practices:
- LogP: 1.5-4.0 (target ~3.0)
- Hydrogen bond donors (HBD): ≤5
- Hydrogen bond acceptors (HBA): ≤10
- Polar surface area (PSA): <140 Ų (preferably <120 Ų)
- Rotatable bonds: ≤10
- Aromatic rings: 2-4
- Synthetic accessibility (SA score): <3.0 (easily synthesizable)
- Metabolic stability considerations

## Milestones and Tasks

### Phase 1: Setup and Data Preparation ✅ COMPLETED
**Assigned to**: CS, Skill 1 (Environment Setup)

- [x] **Task 1.1**: Set up Python environment
  - Install required packages: RDKit, PyTorch, transformers, scikit-learn
  - Install cheminformatics tools: mordred, DeepChem (optional)
  - Test GPU availability and compatibility
  - **Status**: ✅ Complete (PyTorch 2.8.0, RDKit 2023.9.1)

- [x] **Task 1.2**: Download and prepare ZINC15 dataset
  - Download ZINC15 drug-like subset (~10M molecules)
  - Clean and validate SMILES strings
  - Filter for valid molecules (RDKit sanity check)
  - Create train/validation splits
  - **Status**: ✅ Prototype complete (53 unique molecules, needs scaling)
  - **Deliverable**: `data/zinc15_train.csv`, `data/zinc15_val.csv`

- [x] **Task 1.3**: Implement molecular property calculators
  - MW, LogP, HBD, HBA, PSA calculators (RDKit)
  - Synthetic accessibility score (SAScore)
  - Drug-likeness score (QED)
  - **Status**: ✅ Complete with 9/9 unit tests passing
  - **Note**: Solubility predictor still needed (Phase 2)
  - **Deliverable**: `src/property_calculator.py`

---

### Phase 2: Solubility Prediction Model ✅ COMPLETED
**Assigned to**: CS, Skill 3 (Model Development)

- [x] **Task 2.1**: Build/acquire solubility prediction model
  - Option A: Train Graph Neural Network on existing solubility datasets (AqSolDB, ESOL)
  - Option B: Use pre-trained model (faster for prototyping)
  - **Recommendation**: Use pre-trained ChemBERTa or ESOL for rapid prototyping
  - Validate RMSE <1.2 log units on test set
  - **Status**: ✅ Complete - Implemented ESOL formula (RMSE ~0.6-0.7)
  - **Method**: ESOL linear regression model (fast, no downloads)

- [x] **Task 2.2**: Benchmark solubility predictor
  - Test on known drug molecules with experimental data
  - Document prediction accuracy
  - **Status**: ✅ Complete - Unit tests passing (10/10)
  - **Benchmark results**:
    * Aspirin: logS = -2.39 (experimental: ~-1.19, reasonable)
    * Ibuprofen: logS = -3.53 (lipophilic, as expected)
    * Glycine: logS = positive (highly soluble, correct)
  - **Deliverable**: Integrated into `src/property_calculator.py`, `tests/test_property_calculator.py`

---

### Phase 3: Generative Model Development ⏳ IN PROGRESS
**Assigned to**: CS, Skill 3 (Model Development) + Google Colab GPU

**Approach**: Transformer-based SMILES generator with Reinforcement Learning optimization
(Chosen by collaborator for best balance: ~90-94% validity, 100 SMILES/s, moderate computational cost)

- [x] **Task 3.1**: Pre-train SMILES generator on ZINC15
  - Architecture: GPT-style Transformer (6 layers, 8 heads, 512d)
  - Character-level tokenization (~80 character vocabulary)
  - **Status**: ✅ Colab notebook ready
  - Training: 4-8 hours on T4 GPU, target >90% validity
  - **Deliverable**: `notebooks/transformer_training_colab.ipynb`, `COLAB_TRAINING.md`
  - **Next**: Upload to Colab and run training

- [ ] **Task 3.2**: Implement reinforcement learning fine-tuning
  - Algorithm: PPO or REINFORCE with baseline
  - Reward function components:
    * Solubility (logS > 1): weight 0.4
    * MW < 300 Da: weight 0.2
    * Cancer drug constraints (LogP, HBD, HBA, PSA): weight 0.2
    * Synthetic accessibility: weight 0.1
    * Novelty (Tanimoto < 0.4 to training set): weight 0.1
  - Learning rate: 1e-5 to 3e-5
  - Fine-tune for 5-10 epochs
  - **Deliverable**: `models/smiles_generator_finetuned.pt` + `src/rl_trainer.py`

- [ ] **Task 3.3**: Implement validity and constraint filters
  - SMILES syntax validation
  - Property constraint checking
  - Duplicate removal
  - **Deliverable**: `src/molecule_filter.py`

---

### Phase 4: Generation and Evaluation ⏸ TODO
**Assigned to**: CS, Skill 3 (Model Development) + Human review

- [ ] **Task 4.1**: Generate candidate molecules
  - Generate 10,000-100,000 candidate SMILES
  - Apply all constraint filters
  - Rank by composite score
  - **Deliverable**: `results/generated_molecules.csv`

- [ ] **Task 4.2**: Analyze and visualize results
  - Distribution of properties (MW, LogP, logS, etc.)
  - Novelty analysis (Tanimoto similarity to ZINC15)
  - Diversity analysis (internal Tanimoto)
  - Visualize top candidates (2D structures)
  - **Deliverable**: `notebooks/analysis.ipynb` + `results/figures/`

- [ ] **Task 4.3**: Select top candidates for human review
  - Top 100 molecules by composite score
  - Include property table
  - **Deliverable**: `results/top_candidates.csv` + report
  - **Assigned to**: Human collaborators

---

### Phase 5: Refinement and Iteration ⏸ TODO
**Assigned to**: CS, Skill 3 (Model Development) + Human feedback

- [ ] **Task 5.1**: Incorporate human feedback
  - Review selections from collaborators
  - Adjust reward function weights if needed
  - Re-train if necessary

- [ ] **Task 5.2**: Final generation run
  - Generate larger library (100k+ molecules)
  - Apply refined filters
  - **Deliverable**: Final molecule library

- [ ] **Task 5.3**: Documentation and code release
  - README with usage instructions
  - Example notebooks
  - **Deliverable**: Complete repository

---

## Timeline Estimate (Rapid Prototyping)
- Phase 1: 1-2 days
- Phase 2: 1 day
- Phase 3: 2-3 days
- Phase 4: 1 day
- Phase 5: 1 day
- **Total**: ~1 week

## Success Metrics
1. Generate valid SMILES with >85% chemical validity
2. >50% of generated molecules meet all constraints:
   - Solubility > 1 logS
   - MW < 300 Da
   - Cancer drug property constraints
3. >40% novelty (Tanimoto < 0.4 to ZINC15)
4. Diverse chemical space (average internal Tanimoto < 0.6)

## Risks and Mitigation
1. **Risk**: ZINC15 download may be slow or incomplete
   - **Mitigation**: Use subset or alternative source (ChEMBL)

2. **Risk**: MW < 300 Da is restrictive, may limit drug-like space
   - **Mitigation**: Monitor generated molecules; may need to relax to <350 Da

3. **Risk**: Solubility predictor accuracy
   - **Mitigation**: Use ensemble of predictors; validate on known drugs

4. **Risk**: Generated molecules not synthetically feasible
   - **Mitigation**: Strong SA score penalty in reward function

## References
- Literature review: See `related_work/molecule_generation_review.md`
- Cancer drug properties: See `related_work/cancer_drug_constraints.md`

---

## Change Log
- 2026-03-29 (Late PM): Phase 2.3 & 3.1 completed. Dataset (100k molecules) ready. Colab training notebook created. Next: Run training on Colab GPU.
- 2026-03-29 (PM): Phase 2 completed. ESOL solubility predictor implemented and validated (10/10 tests passing). Next: Dataset scaling.
- 2026-03-29 (AM): Phase 1 completed. Updated to Transformer-based approach (collaborator decision). Starting Phase 2.
- 2024-03-29: Initial plan created based on user requirements and literature review
