# docs/training_data/

## LUMINARK AI Security Intelligence Training Assets

This directory contains reference and training data for LASE's Guardian AI safety layer (`apps/guardian/`).

### Files

| File | Lines | Purpose |
|------|-------|---------|
| `cybersecurity_encyclopedia.md` | 4,538 | Complete cybersecurity threat knowledge base compiled specifically for LUMINARK AI Security Intelligence Training |

### cybersecurity_encyclopedia.md

**Title:** THE ULTIMATE CYBERSECURITY ENCYCLOPEDIA  
**Subtitle:** Every Threat, Every Scam, Every Attack Vector — Past, Present & Future  
**Compiled for:** LUMINARK AI Security Intelligence Training

**10 Parts:**
1. Foundational Psychology — Why Attacks Work (cognitive biases, Cialdini's 6 principles)
2. Social Engineering — The Human Attack Vector (phishing, pretexting, deepfakes)
3. Technical Attacks — Malware, Viruses & Exploits (ransomware, zero-days, supply chain)
4. Identity Theft & Financial Fraud
5. Advanced Persistent Threats (APTs)
6. Emerging Threats — AI, Deepfakes & Quantum
7. Physical Security Breaches
8. Defensive Strategies & Detection
9. Future Threat Landscape
10. LUMINARK Integration (SAP stage mapping to threat psychology)

**Integration with LASE:**  
Part 10 (LUMINARK Integration) maps threat psychology to SAP stages, enabling the Guardian AI to classify threats not just by technical category but by the SAP stage of the attacker's approach and the defender's vulnerability window. Stage 8 (Illusion of Permanence) is the primary attack surface in social engineering — "your account/system is permanently secure" creates the opening.

**Usage:**  
Feed to LuminarkBeast (`engine/luminark_beast.py`) as training data to create a security-aware language model that reasons through SAP stage dynamics, or use as a static reference for the Guardian AI's threat classification rules (`apps/guardian/luminark/principles.py`).
