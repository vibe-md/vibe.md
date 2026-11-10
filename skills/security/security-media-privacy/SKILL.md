---
name: security-media-privacy

description: "Read-only audit of image and video privacy, covering anonymization, EXIF/GPS metadata sanitization, temporary media files, and uploads to external APIs. Use when code captures, processes, uploads, streams, or stores camera frames, photos, or video, especially before sending media to an API or multimodal AI model. Not for prompt-injection, agent-tool security, RAG, or vector-database isolation reviews; use security-agent-guard for those."
metadata:
  collection: vibe.md
  group: security
  author: Yael Tamari
---

# Security Media Privacy

A read-only security review for code that captures, processes, uploads, streams, or stores images and video.

The goal is to identify privacy risks involving identifiable people, sensitive visual information, image metadata, temporary media files, and external transmission.

This skill should make security reviews understandable and actionable for both experienced developers and users with limited programming knowledge.

Explain findings in clear language. A user should understand what the risk is, why it matters, what information could be exposed, and what to do next.

Include exact technical evidence and practical remediation guidance whenever the available source code supports it.

This skill reviews source code. It does not certify that an application is secure, guarantee anonymization, or replace runtime security testing, privacy assessments, or legal review.

## When to Use

Use this skill when a user asks to:

- Check whether webcam, camera, photo, or video processing protects privacy.
- Review image or video uploads before they are sent to an API, cloud service, or multimodal AI model.
- Check whether uploaded images expose GPS coordinates, device details, timestamps, or other EXIF metadata.
- Audit code that captures, processes, stores, streams, or transmits visual media.
- Check whether raw camera frames or original images are stored or transmitted without appropriate protection.
- Review temporary media files, caches, or storage locations for privacy risks.
- Explain media-privacy risks in a project in beginner-friendly language.

Example user requests:

- "Is my webcam upload safe?"
- "Check my image upload privacy."
- "Can these photos reveal my location?"
- "Review my camera processing code."
- "Does my application upload unblurred camera frames?"
- "Are temporary image files cleaned up properly?"
- "תבדוק אם העלאת התמונות שלי מאובטחת."
- "האם התמונות שאני שולח ל-AI חושפות מידע אישי?"
- "האם המערכת שלי מסירה את נתוני המיקום מהתמונות?"

### Do Not Use This Skill For

- General prompt injection, malicious instructions, or agent tool-call security reviews.
- RAG security, vector-database tenant isolation, or cross-user retrieval leaks.
- Long-term AI memory isolation or memory poisoning.
- Secrets, API-key exposure, dependency vulnerabilities, or general infrastructure security.

For prompt-injection, agent-security, RAG, and vector-database isolation reviews, hand off to `security-agent-guard`.

For secret scanning or committed API keys, hand off to `secret-guard` or `pre-commit-security-review`.

## Examples

- **User:** "Is my webcam upload safe?"

  **Use the skill to:** Trace the camera frame through anonymization, storage, and upload, then report any concerns with exact code locations.

- **User:** "Can these photos reveal my location?"

  **Use the skill to:** Inspect how uploaded images are processed and stored, and check whether sensitive metadata such as GPS coordinates is removed before sharing.

- **User:** "My application sends users' photos to a multimodal LLM. Is that safe?"

  **Use the skill to:** Review the media-handling pipeline, including anonymization, metadata handling, storage, and external transmission. Review media privacy only. If the user asks about prompt injection or the model's handling of malicious instructions, hand off that part to `security-agent-guard`.

For illustrative vulnerable patterns, safer approaches, and suggested tests, see [Media Privacy Reference Vulnerabilities & Fixes](references/examples.md).

## Prerequisites

- **Read-only:** Inspect source code and configuration only. Do not edit, create, delete, or rewrite project files.
- No external network access, credentials, camera access, or real user media is required.
- Do not run the application, upload files, call external APIs, or access a live camera as part of this audit.
- Use source code, configuration, and existing tests as evidence.
- If the workspace cannot be inspected, explain what access or files are missing and ask for the smallest useful input.

## Scope and Audit Checkpoints

Trace the media data flow from its source to each place it is processed, stored, logged, cached, or transmitted.

Do not decide that a system is safe or unsafe based only on the presence or absence of a particular library or function name.

### 1. Frame and Image Anonymization

Inspect whether media containing identifiable people or sensitive visual details is appropriately protected before each relevant storage or external-transmission step.

Look for:

- Camera and video capture APIs, such as OpenCV `cv2.VideoCapture`, browser camera streams, HTML Canvas, and video-processing libraries.
- Face detection, blurring, masking, cropping, redaction, or other anonymization steps.
- Whether protection is applied before the original frame is saved, logged, cached, or sent elsewhere.
- Whether a failure in detection or anonymization causes the system to fail safely rather than silently sending the unprotected original.
- Whether the code accidentally sends the raw frame while also creating a separate blurred copy.
- Whether all relevant faces and sensitive visual details are considered.
- Whether the anonymized output is the actual object passed to the next processing or upload function.

Do not assume that calling `GaussianBlur`, detecting a face, or using a function named `anonymize` proves that people are protected.

Check the actual data flow. Trace the original frame and every derived copy separately.

If the source code is insufficient, report the result as **Not verified**.

Blurring the whole frame may reduce visual detail but is not automatically a reliable anonymization method.

Do not require face blurring for every image. Consider the purpose, data, user expectations, and whether identifiable people or sensitive details are present.

### 2. EXIF and Image Metadata

Inspect image-ingestion and image-export paths for metadata that may disclose private information.

Look for:

- EXIF GPS coordinates and location information.
- Capture timestamps and time-zone information.
- Camera make, model, and device identifiers.
- Other metadata that could identify a person, device, or location.
- Whether metadata is removed or deliberately preserved before the image is stored or shared.
- Whether the sanitized image, rather than the original upload, is subsequently saved or transmitted.
- Whether the chosen image library and output format actually produce a new file without the original metadata.
- Whether metadata may be reintroduced during image conversion, resizing, or export.

Do not assume that opening and saving an image removes all metadata.

Do not assume that removing EXIF automatically removes every possible form of image metadata.

If the code path or library behavior cannot be confirmed from the available evidence, report **Not verified** and explain what should be tested.

### 3. Temporary Media Files and Retention

Inspect how raw and processed media are held during and after processing.

Look for:

- Temporary files, cache directories, local uploads, debug dumps, logs, and persistent storage.
- Whether raw media is retained longer than necessary.
- Whether temporary files are removed on both success and error paths, for example with `finally` or a context manager.
- Whether storage locations have appropriate access restrictions and encryption where required by the application's threat model.
- Whether cleanup can fail silently or leave additional copies behind.
- Whether temporary files use predictable names or shared paths that could cause collisions or unintended access.
- Whether original media remains in backups, archives, or secondary storage locations.

Do not report an in-memory frame or byte buffer as an unencrypted disk file.

Distinguish memory, temporary disk storage, application storage, and remote storage.

Do not claim that deleting a file guarantees secure erasure from every filesystem, backup, or storage layer.

### 4. External Transmission and Data Minimization

When media is sent to an external service, inspect:

- Whether the destination is identifiable and expected.
- Whether transport uses HTTPS.
- Whether only the necessary, appropriately protected media is transmitted.
- Whether the code sends the original media when a sanitized version should be used.
- Whether request logging, error reporting, or retries could expose the media or retain copies.
- Whether the application sends more image data than the requested operation requires.
- Whether the code clearly separates media processing from external transmission.
- Whether error handling can accidentally retry an upload with the original, unprotected media.

Do not claim that HTTPS makes an upload privacy-safe.

HTTPS protects data in transit; it does not remove sensitive content or control what the receiving service retains.

Do not assume that an external API is trustworthy merely because it uses HTTPS.

If the destination's retention policy, access controls, or processing behavior cannot be established from the source code, clearly state that limitation.

## Execution Workflow

Follow these steps when conducting an audit:

1. **Understand the user's goal.** If useful, summarize in one sentence which media flow is being reviewed.

2. **Identify relevant files.** Search for capture, image-processing, upload, storage, metadata, and transmission code. Keep the review focused on those paths.

3. **Identify media sources.** Locate where original images or frames enter the application, including camera APIs, user uploads, and generated media.

4. **Trace each data flow.** Follow the original media and any sanitized copies through processing, logging, temporary storage, persistent storage, and external requests.

5. **Inspect security boundaries.** Determine which operations happen locally and which send data to another service or component.

6. **Collect evidence.** For every finding, record the exact file path, line range, relevant code, and the data-flow reason the behavior is risky.

7. **Assess severity and confidence.** Use the definitions below. Do not invent line numbers or infer behavior that the code does not establish.

8. **Recommend a fix.** Provide a specific, minimal example that fits the language and libraries already used when possible. Clearly label illustrative or incomplete code.

9. **Explain limitations.** Identify relevant code that was unavailable, behavior that could not be verified statically, and tests a developer should run separately.

10. **Summarize for the user.** Start with a plain-language result, then provide technical details and prioritized next steps.

11. **Respect the read-only boundary.** Do not modify the project. Present proposed code changes as suggestions for the developer to apply.

## Severity and Confidence

Use these labels consistently:

### Severity

- **HIGH:** There is clear evidence that identifiable or sensitive media, or sensitive metadata, is exposed to an unintended party or stored in an inadequately protected location with meaningful privacy impact.
- **MEDIUM:** A plausible privacy weakness exists, but exploitability, exposure, or impact depends on configuration or runtime behavior.
- **LOW:** A limited privacy-hardening issue with a smaller or less direct impact.
- **INFO:** A useful observation or recommended improvement that is not a confirmed vulnerability.

### Confidence

Confidence describes the strength of the evidence, not the severity:

- **HIGH:** The relevant data flow and risky behavior are directly visible in the inspected code.
- **MEDIUM:** The code suggests a risk, but an important implementation detail or runtime behavior is not visible.
- **LOW:** The concern is tentative and needs more evidence.

If evidence is insufficient, use **Not verified** rather than presenting an assumption as a confirmed vulnerability.

Do not inflate severity to make the report sound more important.

A HIGH-severity finding does not automatically require HIGH confidence. Report both independently.

## User-Friendly Reporting Requirements

- Begin with a short summary in plain language. Avoid unexplained jargon.
- Explain what information could be exposed, where it could go, and why that matters.
- Show the exact file and line numbers when available.
- Separate confirmed findings from things that could not be verified.
- For each finding, provide a practical fix and explain why it helps.
- If no issue is found, say: "No issues were identified in the code reviewed." Do not say "The application is secure."
- Never claim that a photo is anonymous, metadata-free, or safe unless the available evidence supports that exact claim.
- Do not shame the user or assume they know security terminology.
- Define terms such as EXIF briefly when first mentioned.
- When the user is not technical, explain the finding before presenting the code.
- Prioritize the most important fixes and distinguish required fixes from optional improvements.
- Do not overwhelm the user with irrelevant technical details.
- Explain what the developer should do next in practical steps.
- If the review is incomplete, state which files or flows were not inspected.
- Do not present suggested code as a verified production fix unless it has actually been tested in the target application.

## Reference Material

For illustrative vulnerable patterns, safer implementation patterns, and suggested tests, read [Media Privacy Reference Vulnerabilities & Fixes](references/examples.md).

Treat the examples as teaching material, not as proof that a project's implementation is secure or as drop-in production code.

When using an example, adapt it to the actual project language, framework, image format, and data flow.

Do not report a vulnerability merely because the code resembles an example.

## Output Format

Use the following structure for every completed audit.

If there are no findings, keep the findings section and state that no issues were identified in the reviewed scope.

If the review is incomplete, explicitly identify the missing evidence and avoid claiming that the application is secure.

# Media Privacy Security Audit Report

## 1. Plain-Language Summary

- **Overall Result:** [Issues found / No issues identified in reviewed code / Review incomplete]
- **What Was Reviewed:** [Short description of the media flow and files]
- **Main Concern:** [Most important result in one or two sentences]
- **Important Limitation:** [What could not be verified, if anything]

## 2. Findings Overview
| ID | Finding | Severity | Confidence | File |
|---|---|---|---|---|
| MP-01 | [Short title] | [HIGH/MEDIUM/LOW/INFO] | [HIGH/MEDIUM/LOW] | [path:line] |

If no findings exist, state:

"No issues were identified in the code reviewed."

This statement applies only to the files and flows actually inspected.

## 3. Detailed Findings

### MP-01 — [Finding Title]

- **Category:** [Anonymization / EXIF metadata / Temporary storage / External transmission]
- **Severity:** [HIGH / MEDIUM / LOW / INFO]
- **Confidence:** [HIGH / MEDIUM / LOW]
- **Location:** `path/to/file.py:10-15`

**What the Code Does:**

[Describe the observed behavior in clear language.]

**Why It Matters:**

[Explain the possible privacy impact. Include what information could be exposed and who might receive it.]

**Evidence:**

```python
# Exact relevant code excerpt; do not fabricate or alter it.
```

**Recommended Fix:**

[Describe the smallest appropriate change.]

**Illustrative Remediation:**

```python
# Provide a language-appropriate example.
# Clearly label placeholders and unimplemented functions.
```

**Why This Fix Helps:**

[Explain how the proposed change reduces the identified risk.]

**Verification:**

[Describe a test the developer can perform using synthetic or non-sensitive test data.]

Repeat this structure for each finding.

## 4. Not Verified / Additional Investigation

List relevant privacy properties that could not be established from static source-code review.

For each item include:

- **What could not be verified:** [Specific behavior or property]
- **Why:** [Missing source code, runtime configuration, external service information, or library behavior]
- **Recommended verification:** [Specific test or information needed]

Do not turn an unverified concern into a confirmed vulnerability.

## 5. Prioritized Remediation Plan

### Required Fixes

List changes needed to address confirmed findings, ordered by severity.

### Recommended Improvements

List useful privacy improvements that are not confirmed vulnerabilities.

### Suggested Tests

List tests that should be performed separately by the application developer.

Use synthetic images and mocked or local test services. Never require real user photos, live camera access, or external uploads as part of this read-only audit.

## 6. Final Assessment

- **Review Scope:** [Files and media flows inspected]
- **Confirmed Findings:** [Number]
- **Unverified Items:** [Number]
- **Highest Severity:** [HIGH / MEDIUM / LOW / INFO / None identified]
- **Overall Conclusion:** [Concise, evidence-based conclusion]

Do not describe the application as fully secure based on a static source-code review.
