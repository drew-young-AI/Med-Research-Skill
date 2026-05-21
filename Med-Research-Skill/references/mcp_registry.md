# Medical MCP Registry & Agentic Skills

This registry tracks all Tool/MCP/Skill integrations available for this workspace. AI Agents (Gemini CLI, Copilot) must check this list before starting deep research or automation tasks.

## 1. Registered Skills
- **med-research**: High-fidelity literature mining (PubMed, Scholar, Consensus).
  - *Status*: Installed (Workspace scope).
  - *Trigger*: `/skills reload`

## 2. Medical & Research MCP Servers
- **PubMed/PMC**: `cyanheads/pubmed-mcp-server`
  - *Capability*: Full-text PMC extraction, MeSH filtering.
- **ClinicalTrials**: `JackKuo666/ClinicalTrials-MCP-Server`
  - *Capability*: Active trial discovery.

## 3. Global Utility Modules (`/utils`)
- **Downloader (`/utils/downloader`)**: Elite Downloader (v7.1) for stealth PDF/HTML capture.
- **Aggregator (`/utils/knowledge_aggregator.py`)**: Local RAG context builder for NotebookLM-like analysis.

## 4. Agentic Trigger Mandate
- **Agent Duty**: When a new research topic is initiated, the Agent **must** verify if the relevant MCP/Skill is installed.
- **Self-Correction**: If a tool is needed but not found, the Agent must provide the exact `gemini skills install` or `npx` command to the user for immediate resolution.
