# Agent Memory: Molecule Design for Solubility

## Project Goal
Develop a molecule design code to generate SMILES structures of new molecules with solubility >1 logS.

## Domain Knowledge

### Literature Review Summary (2023-2024)
Based on comprehensive research, current state-of-the-art approaches include:

#### Model Architectures
1. **RNN (LSTM/GRU)**
   - Validity: 85-88%, Novelty: 45-55%
   - Fast generation: 1000 SMILES/s
   - Good for rapid prototyping, smaller datasets
   
2. **Transformers** (RECOMMENDED for balance)
   - Validity: 90-94%, Novelty: 50-60%
   - Moderate speed: 100 SMILES/s
   - Best balance of performance and computational cost
   - Suitable for medium-throughput optimization
   
3. **Diffusion Models**
   - Validity: 92-96%, Novelty: 60-65%
   - Slow: 0.5-2s per SMILES
   - Highest quality but expensive (requires 16GB+ GPU, 1000+ GPU-hours training)

#### Optimization Strategies
1. **Reinforcement Learning** (property-guided)
   - Fine-tune pre-trained generator with reward function
   - Composite reward: predicted logS + drug-likeness + synthetic accessibility
   - Algorithms: PPO or REINFORCE
   - Improvement: 0.4-0.6 log units in solubility
   
2. **Multi-Objective Bayesian Optimization**
   - Uses VAE latent space + Gaussian Process
   - Optimizes multiple properties simultaneously
   - Improvement: 0.8 log units while maintaining QED ≥0.6
   
3. **Genetic Algorithms**
   - Direct SMILES mutation and crossover
   - Simple but lower validity rates (~85%)
   - Good for smaller-scale projects

#### Recommended Datasets
- **ZINC15**: 10M drug-like molecules (most common baseline)
- **PubChem**: 111M compounds (broad coverage but noisy)
- **ChEMBL**: 2.3M bioactive molecules (with activity annotations)

#### Key Implementation Considerations
- Need solubility predictor (QSAR model or GNN)
- SMILES validity checking is critical
- Trade-offs: validity vs. novelty vs. computational cost
- Synthetic accessibility scoring recommended
- Consider drug-likeness filters (e.g., Lipinski's rules)

## User Requirements (Confirmed)
1. **Application**: Cancer drug discovery
2. **Primary constraint**: Solubility > 1 logS
3. **Molecular weight**: < 300 Da (more restrictive than typical 300-600 Da)
4. **Scale**: Generate as many valid candidates as possible
5. **Dataset**: ZINC15 (10M drug-like molecules)
6. **Timeline**: Rapid prototyping
7. **Resources**: GPU available

## Cancer Drug Design Constraints (Literature-based)
Typical properties for oncology small molecules:
- **LogP**: 1.5-4.0 (optimal ~3.0 for membrane permeation)
- **Hydrogen bond donors (HBD)**: ≤5
- **Hydrogen bond acceptors (HBA)**: ≤10
- **Polar surface area (PSA)**: <140 Ų (preferably <120 Ų for oral absorption)
- **Rotatable bonds**: ≤10 (for binding entropy and metabolic stability)
- **Aromatic rings**: 2-4 (for kinase binding)
- **Synthetic accessibility**: SA score <3.0 (easily synthesizable)
- **Caco-2 permeability**: Papp >10 × 10⁻⁶ cm/s
- **Metabolic clearance**: HLM <20 µL/min/mg
- **Oral bioavailability**: Target >30% (though 10-20% acceptable for potent drugs)

### Key Considerations
- MW <300 Da is quite restrictive (typical range 300-600 Da) but achievable
- Higher solubility (>1 logS) is beneficial for cancer drugs
- Need to balance lipophilicity for cell permeability vs. solubility
- Synthetic accessibility critical for rapid lead development

## Implementation Strategy
**Chosen approach**: LSTM-based SMILES generator with Reinforcement Learning
- **Rationale**: Best balance for rapid prototyping (faster than Transformers/Diffusion, better than pure RNN)
- **Optimization**: Multi-objective reward function with property constraints
- **Expected output**: 10k-100k candidate molecules with >85% validity

## Next Steps
✅ Goal refined and confirmed
✅ Literature review completed
✅ Research plan created (PLAN.md)
⏳ Starting Phase 1: Environment setup and data preparation
