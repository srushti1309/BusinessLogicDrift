# Quantifying and Repairing Business Logic Drift in Legacy to Microservices Migration

## Project Overview

This project presents a research-oriented, AI-assisted framework for **detecting, quantifying, analyzing, and repairing business logic drift** that may occur during the migration of legacy software systems to modern microservices-based architectures.

Migrating a legacy application to microservices involves more than restructuring code or separating functionality into independent services. During this process, existing business rules, validation conditions, calculations, database operations, and execution workflows may be unintentionally modified.

Even when the modernized system produces the same output as the legacy application, its internal behavior may differ. Such differences can affect data consistency, transaction processing, workflow execution, and the correctness of business operations.

The primary objective of this project is to develop a systematic approach for identifying these differences, measuring their severity through a **Logic Drift Index (LDI)**, and assisting developers in generating and verifying corrective changes.

The framework combines static code analysis, automated boundary testing, multidimensional behavioral comparison, quantitative drift measurement, and AI-assisted repair recommendations.

---

## Problem Statement

Traditional software migration validation often focuses on functional testing, API responses, and output equivalence.

However, two implementations may return identical results while performing different internal operations.

For example, consider an order-processing application migrated from a legacy system to a microservices architecture.

Both implementations may return:

`Order processed successfully`

However, the modernized implementation might:

- Skip an inventory update at a specific discount threshold.
- Record an incorrect order status.
- Execute business operations in a different sequence.
- Handle exceptions or transactions differently.

These inconsistencies may remain undetected by conventional output-based testing.

This project addresses the need for a more comprehensive approach that examines both externally visible results and instrumented internal behavior.

---

## Objectives

The major objectives of this project are:

1. Analyze business rules in legacy and modernized implementations using Abstract Syntax Tree (AST) analysis.
2. Identify potential differences in conditional expressions, comparison operators, and business-rule structures.
3. Automatically generate boundary-oriented test cases for supported operations.
4. Execute equivalent test scenarios against legacy and modernized implementations.
5. Compare outputs, application state, database changes, exceptions, workflow traces, and transaction events.
6. Quantify observed behavioral divergence using a weighted Logic Drift Index.
7. Identify potential source-level locations associated with detected drift.
8. Assist in generating corrective code changes.
9. Verify proposed repairs through differential execution and regression testing.
10. Gradually extend the framework toward more realistic legacy-to-microservices migration scenarios.

---

## Current Prototype Implementation

The current prototype consists of several interconnected modules that together provide a controlled workflow for detecting and evaluating business logic drift.

### 1. Static Code Analysis

The framework uses Python's built-in Abstract Syntax Tree (AST) module to analyze source code.

It extracts structural information about business rules, including:

- Conditional statements.
- Comparison operators.
- Numerical thresholds.
- Variable assignments.
- Source-code locations.
- Potentially affected variables.

A rule-matching component compares extracted rules from legacy and modernized implementations to identify candidate correspondences and possible structural differences.

These matches are treated as hypotheses requiring further behavioral validation rather than definitive proof of equivalence.

**Implementation status:** Implemented and tested for supported Python code patterns.

### 2. Automated Boundary Test Generation

The prototype generates test inputs around numerical thresholds identified during static analysis.

For example, a condition involving a threshold of `1000` can produce tests for:

- `999` — below the threshold.
- `1000` — exactly at the threshold.
- `1001` — above the threshold.

This approach helps expose subtle migration defects, particularly those caused by changes in comparison operators such as `>` and `>=`.

**Implementation status:** Implemented for supported numerical comparisons. Broader path coverage and complex input generation remain future work.

### 3. Multidimensional Behavioral Execution

The prototype includes a controlled execution framework for comparing equivalent operations in legacy and modernized implementations.

Rather than examining only return values, it records multiple behavioral dimensions:

**Output behavior:** Differences in returned values or response structures.

**Application state:** Differences in observable state before and after execution.

**Database behavior:** Changes in database records and persisted values, currently demonstrated using SQLite fixtures.

**Exception behavior:** Differences in errors raised during execution.

**Workflow behavior:** Differences in instrumented business-operation sequences.

**Transaction behavior:** Differences in recorded transaction events, including commits and rollbacks.

The execution framework runs supported operations against independent database fixtures to prevent test contamination.

**Implementation status:** Implemented and tested using trusted, instrumented Python operations. Arbitrary project execution and external microservice instrumentation are not yet supported.

### 4. Logic Drift Index (LDI)

A central component of the project is the **Logic Drift Index**, a weighted metric designed to quantify observed differences between legacy and modernized implementations.

The current prototype uses four primary dimensions:

| Dimension | Weight |
|---|---:|
| Output divergence | 40% |
| State divergence, including database observations | 25% |
| Exception divergence | 20% |
| Workflow divergence, including transaction observations | 15% |

The current calculation is:

**LDI = (100 / N) × Σ [0.40(Do) + 0.25(Ds) + 0.20(De) + 0.15(Dw)]**

Where:

- **N** represents the number of evaluated test cases.
- **Do** represents output divergence.
- **Ds** represents state divergence.
- **De** represents exception divergence.
- **Dw** represents workflow divergence.

The metric produces a score between 0 and 100 when the required observations are available.

A score of zero indicates no divergence detected across the evaluated dimensions and test scenarios. It does not guarantee complete behavioral equivalence.

The current weights and severity thresholds are provisional research parameters that will require further validation.

**Implementation status:** Implemented with multidimensional scoring, coverage handling, and severity interpretation.

### 5. Drift Localization

The framework combines static rule differences with observed behavioral divergence to identify potential areas for investigation.

Candidate localization records include source locations, rule-matching information, and associated analysis-level evidence.

At present, localization is exploratory. The framework does not claim that every identified rule is the proven cause of an observed difference.

**Implementation status:** Preliminary candidate localization implemented. Causal localization and more precise ranking remain future work.

### 6. Repair Candidate Generation

The prototype includes an AST-based patching component capable of generating targeted comparison-operator modifications.

For example:

`amount > 1000`

may be proposed for modification to:

`amount >= 1000`

The framework can also use a locally hosted AI coding model through Ollama to provide advisory analysis and repair suggestions.

The current repair process is deliberately controlled. It does not automatically execute arbitrary AI-generated source code or deploy changes to the original application.

**Implementation status:** Targeted operator patch generation and AI advisory components implemented. Generalized AI-driven repair orchestration is planned.

### 7. Multidimensional Repair Verification

A major capability of the prototype is evaluating whether a proposed repair actually improves behavioral consistency.

The verification process compares:

- Legacy versus original modernized behavior.
- Legacy versus candidate-repaired behavior.

Both comparisons use equivalent test cases and independently initialized database fixtures.

The framework then examines LDI changes and identifies regressions.

A candidate may be rejected even if it fixes one failing test case, because it introduces behavioral differences elsewhere.

**Implementation status:** Regression-aware repair verification implemented and tested. A stricter verification extension for dimension-level regression checks and successful repair demonstration is the next development stage.

---

## Experimental Prototype: Order Processing Scenario

The current experimental scenario uses a controlled order-processing application implemented in two versions:

- **Legacy implementation:** Represents the reference business behavior.
- **Modernized implementation:** Contains intentionally introduced migration defects.

The scenario includes discount calculations, inventory reservation, order creation, database updates, workflow events, and transaction handling.

### Seeded Migration Defect

At an order amount of ₹1,000, the modernized implementation skips inventory reservation and records an incorrect order status.

However, both implementations return the same successful output.

This demonstrates why output-only testing may fail to detect important business logic drift.

### Observed Results

The multidimensional analysis detected differences in application state, database behavior, and workflow execution at the threshold.

| Test case | Order amount | LDI |
|---|---:|---:|
| TC001 | ₹999 | 0 |
| TC002 | ₹1,000 | 40 |
| TC003 | ₹1,001 | 0 |

**Overall baseline LDI: 13.333333**

### Regression-Aware Repair Experiment

A deliberately incomplete repair was generated and evaluated.

Although the candidate improved the ₹1,000 scenario, it introduced a new regression at ₹1,001.

The observed results were:

| Metric | Result |
|---|---:|
| Baseline LDI | 13.333333 |
| Candidate LDI | 21.666667 |
| Improved test cases | 1 |
| Regressed test cases | 1 |
| Candidate accepted for review | No |

The framework correctly rejected this candidate because the repair increased overall behavioral divergence.

This experiment demonstrates that repair verification must consider both improvements and newly introduced defects.

---

## Current Development Status

**Status: Functional research prototype — active development**

The prototype currently includes:

- Python AST parsing and business-rule extraction.
- Candidate rule matching.
- Automated numerical boundary test generation.
- Controlled differential execution.
- Application state and SQLite database observation.
- Exception, workflow, and transaction-event comparison.
- Multidimensional Logic Drift Index calculation.
- Preliminary drift localization.
- Targeted AST-based repair generation.
- Local AI-assisted repair advisory integration.
- Regression-aware repair verification.
- Structured JSON analysis and repair reports.
- Automated unit and integration tests.

### Testing Status

The latest confirmed milestone completed **67 automated tests successfully**.

These tests cover the implemented analysis, execution, scoring, and repair-verification components.

Additional tests for the next repair-verification milestone have been prepared, but their results are not yet included in this confirmed count.

The current prototype demonstrates the core feasibility of the proposed approach under controlled conditions. It is not yet a production-ready migration validation platform.

---

## Technology Stack

| Component | Technology |
|---|---|
| Primary programming language | Python |
| Static analysis | Python AST |
| Automated testing | Pytest |
| Database experimentation | SQLite |
| Behavioral execution | Custom Python execution and recording modules |
| Quantitative analysis | Custom LDI calculator |
| AI-assisted suggestions | Ollama with Qwen2.5-Coder |
| Repair generation | AST-based patching |
| Reporting | JSON |
| Development environment | Visual Studio Code |

---

## Future Development Roadmap

### Phase 1 — Complete Repair Verification

The immediate next stage focuses on demonstrating a successful repair that resolves the seeded order-processing defects without introducing regressions.

Planned improvements include:

- Complete multidimensional verification of successful repairs.
- Per-dimension regression checks.
- Validation of critical business invariants.
- Expanded boundary and negative test coverage.
- Improved source-preserving patch generation.

### Phase 2 — AI-Assisted Repair Orchestration

The framework will be extended to connect AI-generated suggestions with a controlled repair pipeline.

The intended workflow is:

**Detect Drift → Analyze Evidence → Suggest Repair → Validate Candidate → Re-execute Tests → Recalculate LDI → Recommend or Reject**

The AI model will assist in proposing changes, while deterministic checks and behavioral evidence will be responsible for evaluating those proposals.

### Phase 3 — Support for More Complex Migration Scenarios

Future work will investigate:

- Multiple interacting business rules.
- More complex application state transitions.
- Database consistency and transaction anomalies.
- Cross-service workflow differences.
- API-level behavioral comparison.
- More realistic microservices communication patterns.
- Different categories of business logic drift.

### Phase 4 — Generalized Project Input and Analysis

The long-term objective is to move beyond predefined experimental fixtures.

Planned capabilities include:

- Accepting separate legacy and modernized project inputs.
- Discovering supported business operations.
- Mapping corresponding operations between implementations.
- Generating more comprehensive tests.
- Analyzing behavior through isolated execution environments.
- Producing traceable evidence for detected differences.

Safe execution and controlled instrumentation will be essential before supporting arbitrary external projects.

### Phase 5 — Visualization and Developer Dashboard

A future dashboard will present:

- Overall and per-test LDI scores.
- Drift severity and observation coverage.
- Rule-matching results.
- Behavioral comparison details.
- Candidate source locations.
- AI-assisted repair suggestions.
- Before-and-after repair evaluations.
- Regression warnings and verification reports.

The goal is to make migration differences understandable and actionable for developers.

### Phase 6 — Experimental Evaluation and Research Validation

The final research stage will evaluate the proposed framework using additional controlled and, where feasible, realistic migration scenarios.

Potential evaluation criteria include:

- Drift detection effectiveness.
- Boundary test coverage.
- False positives and false negatives.
- Localization accuracy.
- Repair success and regression rates.
- Execution overhead.
- LDI sensitivity to dimension weights.
- Applicability across different migration scenarios.

These experiments will help determine the framework's strengths, limitations, and practical usefulness.

---

## Expected Contribution

This project aims to contribute an integrated approach to business logic preservation during software modernization.

Its central contribution is the combination of:

1. **Structural analysis** to identify potential business-rule differences.
2. **Multidimensional execution evidence** to observe differences beyond return values.
3. **Quantitative drift measurement** through the Logic Drift Index.
4. **Repair evaluation** that considers both corrected behavior and newly introduced regressions.
5. **AI-assisted development support** under deterministic verification and human review.

The intended outcome is a framework that helps developers make migration decisions based on measurable behavioral evidence rather than relying solely on successful compilation or matching API responses.

---

## Limitations

The current prototype has several important limitations:

- Behavioral execution requires trusted, instrumented operations.
- Static rule matching does not establish semantic equivalence.
- Generated boundary tests do not guarantee complete path coverage.
- External microservice calls are not yet comprehensively observed.
- Repair verification applies only to the executed test scenarios.
- LDI weights and severity thresholds require empirical validation.
- Candidate localization is not yet causally proven.
- AI-generated suggestions are advisory and require validation.
- Production deployment and autonomous code modification are outside the current prototype's scope.

These limitations define the next areas of development and research.

---

## Conclusion

The current prototype establishes an initial end-to-end foundation for detecting and measuring business logic drift during legacy-to-microservices migration.

It demonstrates that two implementations can produce identical outputs while differing in database state, application state, and workflow behavior.

It also demonstrates that proposed repairs must be evaluated carefully: correcting one defect does not necessarily improve overall system consistency.

The next stages will focus on successful repair verification, AI-assisted repair orchestration, broader migration scenarios, stronger testing, and an interactive analysis dashboard.

**The long-term goal is to build a reliable, explainable, and evidence-driven framework for detecting, quantifying, and repairing business logic drift while preserving the intended behavior of legacy applications during modernization.**
