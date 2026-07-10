# Universal Research Mandate (Med Deep Research v5.3)

This document defines the unified logic for ALL AI Agents (Gemini, Copilot, Claude) working on this project.

## 1. Academic Rigor
- **Source Verification**: Only trust JCR Q1/Q2 journals for foundational claims.
- **Data Scrutiny**: Distinguish between "Instrument Validity" (e.g., expert agreement) and "Model Performance" (e.g., AUC/Accuracy).
- **Mandatory Metrics**: Always cite Impact Factor (IF) and Quartile.

## 2. Research Protocol (GARP v5.0)
- **Step 1**: Search PubMed (Clinical) and Google Scholar (Breadth).
- **Step 2**: Apply AI-Consensus logic (Categorize as Support/Oppose/Neutral).
- **Step 3**: Archive all findings locally in `/papers` using [Year_Title_Author] format.

## 3. Tool Mapping
- **Gemini CLI**: Execute `med-research` skill.
- **Copilot CLI**: Refer to `.github/copilot-instructions.md`.
- **General Agents**: Access logic via Python clients in `Med-Research-Skill/med-research/scripts/`.
