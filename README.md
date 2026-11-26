# LUMINARK Axiom Systems Engine (LASE)

**Status: multi-component development repository; integration and external validation remain in progress.**

LASE is a consolidated code repository containing parts of the LUMINARK / SAP ecosystem. It includes a shared core, multiple engine builds, application directories, domain adapters, test suites, data files, and documentation.

This repository should be understood as an engineering workspace and prototype collection—not as proof that every component is integrated, production-ready, scientifically validated, or commercially deployable.

## Repository areas

- `core/`: shared types, NSDT calculations, stage logic, adapters, and core tests.
- `engine/`: stage-energy and related engine components.
- `apps/`: application-specific code, including Guardian, Axiom Yield, Metatron, and an Overwatch demonstration.
- `build1_overwatch_strict/` through `build4_unified_field/`: distinct engine and application builds.
- `data/`, `baseline/`, `results/`, and `audit_results/`: datasets, generated outputs, and analysis artifacts.
- `docs/`: architecture and technical notes.

## How to interpret tests and data

Automated tests can check that code follows its own formulas, constants, interfaces, and expected examples. Passing unit or invariant tests does not establish that a model predicts real-world events accurately.

The repository includes demonstration scenarios and baseline/validation-related files. Their provenance, data quality, labeling, reproducibility, independence, and suitability for external claims still need review. No general predictive accuracy, cross-domain validation rate, or customer outcome should be inferred from the presence of these files.

Before describing LASE as a unified production engine, each application and engine path needs reproducible build and integration testing, dependency review, security review, and clear identification of the canonical implementation.

## Conceptual provenance

The project owner states that the underlying concepts, product idea, and 0-9-0 / SAP framework applications in this repository originated with him. AI systems generated the implementation code and suggested technical mechanisms used to express those concepts. NSDT and the Container Rule were introduced by AI as supporting implementation mechanisms within the owner's framework, not as independent conceptual origins.

This records the project owner's account; it is not a legal determination of copyright ownership, inventorship, or exclusive rights.

## Patent and legal status

**No patent application has been filed for LASE or the projects described in this repository.** Patent-related documents or folders, where present, are unfiled working materials and do not establish patent rights or a pending application.

The repository owner has disclosed AI-assisted development. Code authorship, human creative contributions, third-party components, open-source licenses, data rights, and model terms require a separate provenance review before commercialization.

## Recommended next steps

1. Identify the canonical engine and document which builds are active, experimental, or superseded.
2. Map copied and modified files back to their source repositories.
3. Run the documented test workflows and preserve the actual results.
4. Separate unit tests from empirical model validation.
5. Audit dependencies, licenses, secrets, APIs, and data rights.
6. Create a small, reproducible demonstration around one clearly defined use case.

No production-readiness, patent-protection, scientific-validation, valuation, or revenue claim is made by this README.
