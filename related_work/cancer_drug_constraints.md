# Cancer Drug Molecular Property Constraints

## Summary
This document outlines typical physicochemical and ADME properties for small-molecule cancer drugs based on systematic literature review (2023-2024).

## Physicochemical Properties

### Molecular Weight
- **Typical range**: 300-600 Da
- **Median (kinase inhibitors)**: ~450 Da
- **Rationale**: Balance between cell permeability and target affinity
- **Challenge**: MW >600 Da faces poor membrane permeation and oral bioavailability

### Lipophilicity (LogP/LogD)
- **Optimal LogP**: 1.5-4.0
- **Average**: ~3.0
- **LogD at pH 7.4**: 2.0-4.5
- **Rationale**: Adequate membrane permeation without high nonspecific binding
- **Warning**: LogP >5 correlates with poor solubility and high metabolic clearance

### Hydrogen Bonding
- **HBD (donors)**: ≤5
- **HBA (acceptors)**: ≤10
- **Rationale**: Lipinski's Rule of Five for oral drug-likeness

### Polar Surface Area (PSA)
- **Target**: <140 Ų for oral absorption
- **Optimal**: <120 Ų
- **CNS penetration**: <90 Ų (if needed)
- **Warning**: 
  - Too low (<50 Ų): reduced solubility
  - Too high (>140 Ų): impaired passive diffusion

### Structural Features
- **Aromatic rings**: 2-4 (for kinase/protein binding)
- **Rotatable bonds**: ≤10 (for binding entropy and metabolic stability)
- **Flexibility**: Macrocyclization or intramolecular H-bonds can enhance permeability

## ADME Characteristics

### Aqueous Solubility
- **Minimum target**: ≥10 µg/mL (≥25 µM) at pH 6.5-7.4
- **Critical threshold**: >1 µg/mL
- **Enhancement strategies**: Salt forms, co-crystals, amorphous dispersions

### Membrane Permeability
- **Caco-2 Papp**: >10 × 10⁻⁶ cm/s (high permeability)
- **Efflux ratio**: <2 (ideally ≈1)
- **Warning**: ER >3 indicates significant P-gp or BCRP involvement

### Metabolic Stability
- **HLM clearance**: <20 µL/min/mg protein
- **Hepatic extraction ratio**: <0.5 (ideally)
- **Strategy**: Bioisosteric replacement, steric shielding of metabolic soft spots

### Pharmacokinetics
- **Half-life (t₁/₂)**: 
  - Once-daily: 12-24 hours
  - Twice-daily: 6-12 hours
- **Oral bioavailability (F)**: >30% ideal, 10-20% acceptable for potent drugs
- **Plasma protein binding**: 85-99% typical for lipophilic agents
- **Volume of distribution**: 0.5-5 L/kg

## Multi-Parameter Optimization (MPO)

Integrated scoring framework for oncology drug candidates:
- **cLogP**: ≤4
- **MW**: ≤550 Da
- **PSA**: ≤120 Ų
- **Predicted clearance**: <20 mL/min/kg

## Synthetic Accessibility
- **SA Score**: <3.0 (easily synthesizable)
- **Rationale**: Rapid lead development and cost-effective manufacturing

## Key Medicinal Chemistry Strategies
1. **Bioisosteric replacement**: Enhance metabolic stability (e.g., F for H, N-methylation)
2. **Conformational restriction**: Macrocycles, intramolecular H-bonds
3. **Strategic ionization**: Weak bases (pKa 6-8) for pH-driven solubility
4. **Early ADME profiling**: High-throughput assays parallel with potency screening

## Case Example: Kinase Inhibitor Optimization
- **Initial**: MW 620 Da, LogP 5.8, PSA 155 Ų, ER 4
- **Optimized**: MW 480 Da, LogP 3.6, PSA ~120 Ų, ER 1.8
- **Result**: 42% oral bioavailability, t₁/₂ 14h, robust tumor growth inhibition

## References
- Literature review conducted March 2024
- Based on systematic analysis of oncology drug design best practices (2023-2024)
