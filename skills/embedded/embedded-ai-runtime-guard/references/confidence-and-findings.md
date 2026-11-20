# Finding Severity, Confidence, and Control Status

Use separate fields for severity, confidence, and control status. They answer different questions.

## 1. Severity

### Critical
A confirmed, direct path can cause potentially severe physical harm or catastrophic system failure, and no effective protection is visible in the inspected scope. Explain the evidence and scope carefully.

### High
A significant safety or runtime control is missing, incomplete, or bypassable, with a credible failure scenario.

### Medium
A weakness can materially reduce reliability, availability, or recovery under defined conditions.

### Low
A limited weakness or defense-in-depth improvement with constrained impact.

### Informational
An observation, documentation gap, or improvement opportunity without an established defect.

Severity must reflect plausible impact and exploit/failure conditions, not keyword presence or confidence alone.

## 2. Confidence

### High
Direct code evidence and the relevant control/data flow are visible. Dependencies needed for the conclusion have been inspected.

### Medium
Strong evidence exists, but one or more dependencies, configuration details, or execution paths are unavailable.

### Low
Visibility is incomplete or material assumptions affect the conclusion.

Confidence is not a probability unless a validated probabilistic calibration method exists. Do not invent percentages.

## 3. Control Status

- `PASS`: evidence supports that the control is implemented for the inspected scope.
- `PARTIAL`: some implementation exists but a material gap remains.
- `FAIL`: evidence demonstrates the required control is absent, bypassed, or ineffective.
- `NOT VERIFIED`: evidence is insufficient; external HAL, hardware, configuration, or runtime behavior may matter.
- `NOT APPLICABLE`: the control does not apply to the inspected architecture.

Do not use `NOT VERIFIED` as a softer synonym for a demonstrated failure. Do not use `NOT APPLICABLE` merely because code was not found.

## 4. Finding Evidence Requirements

Every actionable finding should include:

- Stable ID, e.g. `EAR-001`.
- Short title.
- Severity, confidence, and control status.
- Exact file and line range, or explain why unavailable.
- Minimal relevant code evidence.
- Traced caller/callee or data path.
- Preconditions and failure scenario.
- Runtime/physical impact, stated without exaggeration.
- Recommended remediation.
- Regression test proposal.
- Dependencies and limitations.

Avoid claims such as "the device will crash" when the evidence only establishes a possible unbounded allocation or missing error branch. Use calibrated language such as "can exhaust the configured heap under repeated execution if no external bound exists."

## 5. False-Positive Controls

Before reporting:

1. Search for wrappers, interfaces, callbacks, HAL implementations, generated code, and configuration that may provide the control.
2. Trace the call site and failure branch rather than relying on symbol names.
3. Check whether allocation is initialization-only, bounded, pooled, or in a critical loop.
4. Check whether a timeout is enforced by the called API or only passed as an unused parameter.
5. Check whether a fallback delegates to a separately implemented controller.
6. Check whether limits are enforced in a lower driver or hardware interlock.
7. Mark uninspected dependencies `NOT VERIFIED`.
8. Do not duplicate one root cause as multiple findings unless impacts or controls are independently actionable.

## 6. Overall Assessment

Summarize the most consequential findings and unverified areas. Do not calculate a numeric safety score unless the project defines a validated scoring method. Never describe the audit as certification or proof of device safety.
