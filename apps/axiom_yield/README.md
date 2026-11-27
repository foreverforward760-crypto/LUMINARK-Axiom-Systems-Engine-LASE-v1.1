# Axiom Yield — Logistics Risk-Scoring Prototype

**Project concept:** Richard Stanfield, according to the project owner  
**Implementation:** AI-generated code developed under the project owner's direction  
**Status:** Experimental prototype; predictive performance has not been established.

Axiom Yield applies the owner's 0-9-0 / Stanfield's Axiom of Perpetuity framework to logistics-related inputs. The repository contains a browser interface, a FastAPI backend, NSDT input normalization, rule-based stage and trap calculations, an ELD connector layer, and demonstration scenarios.

## What is implemented

- Browser-based logistics dashboard and scoring interface.
- FastAPI endpoints for carrier and route input processing.
- NSDT adapter that maps selected route, hours-of-service, recovery, market, and communication inputs into five normalized dimensions.
- Rule-based stage, trap-energy, and signal-translation logic.
- ELD connector code; connector coverage and live-data behavior require independent verification.
- Demonstration scenarios and automated tests for selected constants, thresholds, and calculation paths.

## What is not established

This codebase does not demonstrate that Axiom Yield predicts carrier failures, accidents, driver departures, fraud, or capacity changes 24–48 hours in advance. Demonstration scenarios are not prospective test results. Passing unit tests establishes only that selected code paths return expected outputs for programmed inputs; it does not establish real-world accuracy, calibration, lead time, or improved dispatch outcomes.

Some input paths may use default or fallback values when live telemetry is unavailable. Outputs based on defaults or incomplete data must not be represented as live carrier intelligence.

No customer traction, revenue, market valuation, acquisition value, or financial return is established by this repository.

## Conceptual foundation and implementation history

The project owner states that the Axiom Yield product idea, its intended logistics application, and the underlying 0-9-0 / SAP framework originated with him. AI systems generated the code and suggested technical mechanisms used to implement those concepts. NSDT and the Container Rule are treated as supporting implementation mechanisms introduced during AI-assisted development within the owner's framework, not as independent conceptual origins.

This records the project owner's account. It is not a legal determination of copyright ownership, inventorship, or exclusive rights.

## Validation required before operational use

1. Obtain verified, permissioned, time-stamped carrier and ELD data.
2. Define the prediction target and time horizon precisely.
3. Separate calibration data from held-out test data.
4. Compare results with appropriate existing logistics baselines.
5. Measure false positives, false negatives, calibration, and lead time.
6. Conduct security, privacy, and integration reviews.
7. Run a prospective pilot with an independent logistics partner.

Do not use prototype scores as the sole basis for dispatch, safety, insurance, credit, or carrier eligibility decisions.

## Running and related source

This directory is the Axiom Yield application copy within the LASE development repository. For the separately maintained application repository, see:

https://github.com/foreverforward760-crypto/AxiomYield

Install the dependencies listed in `backend/requirements.txt` and follow the setup instructions in the application repository. Use synthetic or authorized test data only.

## Patent and rights status

No patent application has been filed for Axiom Yield. Patent-related working notes, if present elsewhere in the ecosystem, do not establish a filed or pending application.

The project owner has disclosed AI-assisted software development. Before licensing or transfer, review the relevant AI-service terms, third-party dependency licenses, human contributions, and rights in all included materials.
