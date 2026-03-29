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

## Questions for User (Goal Refinement)
Waiting for clarification on:
1. Application context (drug discovery, materials, etc.)
2. Additional molecular constraints beyond solubility
3. Scale (number of molecules to generate)
4. Reference datasets availability
5. Computational resources available
6. Preference for generative approach

## Next Steps
- Finalize goal based on user responses
- Create detailed research plan (PLAN.md)
- Set up development environment
- Implement chosen architecture and optimization strategy
