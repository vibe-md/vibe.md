
---
name: security-media-privacy
description: "Use when reviewing code that captures, processes, uploads, streams, or stores camera frames, photos, or video, especially before sending media to an API or multimodal AI model. Trigger for requests such as 'check my webcam privacy', 'audit image uploads', 'does this photo upload expose GPS?', or 'review camera-frame handling'. If a code review already reveals a media-handling pipeline, proactively offer this read-only audit even if the user did not explicitly ask for a security audit. Not for general prompt-injection, agent-tool security, RAG, or vector-database isolation reviews; use security-agent-guard for those."
metadata:
  collection: vibe.md
  group: security
  author: Yael Tamari
---

# Security Media Privacy

A read-only security review for code that captures, processes, uploads, streams, or stores images and video.

The goal is to identify privacy risks involving identifiable people, sensitive visual information, image metadata, and temporary media files.

Explain findings in clear language. A user should understand what the risk is, why it matters, and what to do next, even if they are not an experienced programmer.

Include exact technical evidence and practical remediation guidance for developers.

This skill reviews source code. It does not certify that an application is secure, guarantee anonymization, or replace runtime security testing or privacy/legal review.

## When to Use

Use this skill when a user asks to:

- Check whether webcam, camera, photo, or video processing protects privacy.
- Review image or video uploads before they are sent to an API, cloud service, or multimodal AI model.
- Check whether uploaded images expose GPS coordinates, device details, or other EXIF metadata.
- Audit code that captures, processes, stores, streams, or transmits visual media.
- Explain media-privacy risks in a project in beginner-friendly language.

Example user requests:

- "Is my webcam upload safe?"
- "Check my image upload privacy."
- "Can these photos reveal my location?"
- "Review my camera processing code."
- "תבדוק אם העלאת התמונות שלי מאובטחת."
- "האם התמונות שאני שולח ל-AI חושפות מידע אישי?"

### Proactive Use

If you are already reviewing a codebase and notice a flow that captures, uploads, streams, or stores camera frames, photos, or video, briefly offer to run this media-privacy audit.

If the user's request clearly includes reviewing that flow for safety, perform the audit without requiring them to know the name of this skill.

Do not interrupt unrelated work or scan unrelated parts of a project just to find a reason to invoke this skill.

Do not imply that the audit runs automatically in every conversation. Follow the user's permission and the environment's access rules.

### Do Not Use This Skill For

- General prompt injection, malicious instructions, or agent tool-call security reviews.
- RAG security, vector-database tenant isolation, or cross-user retrieval leaks.
- Secrets, API-key exposure, dependency vulnerabilities, or general infrastructure security.

For prompt-injection, agent-security, RAG, and vector-database isolation reviews, hand off to `security-agent-guard`.

For other security areas, use the repository's relevant security skill.

## Examples

- **User:** “Is my webcam upload safe?”
  **Use the skill to:** Trace the camera frame through anonymization, storage, and upload, then report any concerns with exact code locations.

- **User:** “Can these photos reveal my location?”
  **Use the skill to:** Inspect how uploaded images are processed and stored, and check whether sensitive metadata such as GPS coordinates is removed before sharing.

For illustrative vulnerable patterns, safer approaches, and suggested tests, see [Media Privacy Reference Vulnerabilities & Fixes](references/examples.md).

## Prerequisites

- **Read-only:** inspect source code and configuration only. Do not edit, create, delete, or rewrite project files.
- No external network access, credentials, camera access, or real user media is required.
- Do not run the application, upload files, call external APIs, or access a live camera as part of this audit.
- If the workspace cannot be inspected, explain what access or files are missing and ask for the smallest useful input.

## Scope and Audit Checkpoints

Trace the media data flow from its source to each place it is stored or sent.

Do not decide that a system is safe or unsafe based only on the presence or absence of a particular library or function name.

### 1. Frame and Image Anonymization

Inspect whether media containing identifiable people or sensitive visual details is appropriately protected **before each relevant storage or external-transmission step**.

Look for:

- Camera and video capture APIs, such as OpenCV `cv2.VideoCapture`, browser camera streams, HTML Canvas, and video-processing libraries.
- Face detection, blurring, masking, cropping, redaction, or other anonymization steps.
- Whether protection is applied before the original frame is saved, logged, cached, or sent elsewhere.
- Whether a failure in detection or anonymization causes the system to fail safely rather than silently sending the unprotected original.
- Whether the code accidentally sends the raw frame while also creating a separate blurred copy.

Do not assume that calling `GaussianBlur`, detecting a face, or using a function named `anonymize` proves that people are protected.

Check the actual data flow. If the source code is insufficient, report the result as **Not verified**.

Blurring the whole frame may reduce visual detail but is not automatically a reliable anonymization method.

Do not require face blurring for every image. Consider the purpose, data, user expectations, and whether identifiable people or sensitive details are present.

### 2. EXIF and Image Metadata

Inspect image-ingestion and image-export paths for metadata that may disclose private information.

Look for:

- EXIF GPS coordinates, timestamps, camera make/model, device identifiers, and other metadata.
- Whether metadata is removed or deliberately preserved before the image is stored or shared.
- Whether the sanitized image, rather than the original upload, is subsequently saved or transmitted.
- Whether the chosen image library and output format actually produce a new file without the original metadata.

Do not assume that opening and saving an image removes all metadata.

If the code path or library behavior cannot be confirmed from the available evidence, report **Not verified** and explain what should be tested.

### 3. Temporary Media Files and Retention

Inspect how raw and processed media are held during and after processing.

Look for:

- Temporary files, cache directories, local uploads, debug dumps, logs, and persistent storage.
- Whether raw media is retained longer than necessary.
- Whether temporary files are removed on both success and error paths, for example with `finally` or a context manager.
- Whether storage locations have appropriate access restrictions and encryption where required by the application's threat model.
- Whether cleanup can fail silently or leave additional copies behind.

Do not report an in-memory frame or byte buffer as an unencrypted disk file.

Distinguish memory, temporary disk storage, application storage, and remote storage.

### 4. External Transmission and Data Minimization

When media is sent to an external service, inspect:

- Whether the destination is identifiable and expected.
- Whether transport uses HTTPS.
- Whether only the necessary, appropriately protected media is transmitted.
- Whether the code sends the original media when a sanitized version should be used.
- Whether request logging, error reporting, or retries could expose the media or retain copies.

Do not claim that HTTPS makes an upload privacy-safe.

HTTPS protects data in transit; it does not remove sensitive content or control what the receiving service retains.

## Execution Workflow

1. **Understand the user's goal.** If useful, summarize in one sentence which media flow is being reviewed.
2. **Identify relevant files.** Search for capture, image-processing, upload, storage, metadata, and transmission code. Keep the review focused on those paths.
3. **Trace each data flow.** Follow the original media and any sanitized copies through processing, logging, temporary storage, persistent storage, and external requests.
4. **Collect evidence.** For every finding, record the exact file path, line range, relevant code, and the data-flow reason the behavior is risky.
5. **Assess severity and confidence.** Use the definitions below. Do not invent line numbers or infer behavior that the code does not establish.
6. **Recommend a fix.** Provide a specific, minimal example that fits the language and libraries already used when possible. Clearly label illustrative or incomplete code.
7. **Explain limitations.** Identify relevant code that was unavailable, behavior that could not be verified statically, and tests a developer should run separately.
8. **Summarize for the user.** Start with a plain-language result, then provide technical details and prioritized next steps.

## Severity and Confidence

Use these labels consistently:

- **HIGH:** There is clear evidence that identifiable or sensitive media, or sensitive metadata, is exposed to an unintended party or stored in an inadequately protected location with meaningful privacy impact.
- **MEDIUM:** A plausible privacy weakness exists, but exploitability, exposure, or impact depends on configuration or runtime behavior.
- **LOW:** A limited privacy-hardening issue with a smaller or less direct impact.
- **INFO:** A useful observation or recommended improvement that is not a confirmed vulnerability.

Confidence describes the strength of the evidence, not the severity:

- **HIGH:** The relevant data flow and risky behavior are directly visible in the inspected code.
- **MEDIUM:** The code suggests a risk, but an important implementation detail or runtime behavior is not visible.
- **LOW:** The concern is tentative and needs more evidence.

If evidence is insufficient, use **Not verified** rather than presenting an assumption as a confirmed vulnerability.

Do not inflate severity to make the report sound more important.

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

## Reference Material

For illustrative vulnerable patterns and safer implementation patterns, read [Media Privacy Reference Vulnerabilities & Fixes](references/examples.md).

Treat the examples as teaching material, not as proof that a project's implementation is secure or as drop-in production code.

## Output Format

Use this structure. If there are no findings, keep the findings section and state that no issues were identified in the reviewed scope.

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

## 3. Detailed Findings

### MP-01 — [Finding Title]

- **Category:** [Anonymization / EXIF metadata / Temporary storage / External transmission]
- **Severity:** [HIGH / MEDIUM / LOW / INFO]
- **Confidence:** [HIGH / MEDIUM / LOW]
- **Location:** `path/to/file.py:10-15`
- **What the Code Does:** [Describe the observed behavior]
- **Why It Matters:** [Explain the possible privacy impact in plain language]
- **Evidence:**

```python
# Exact relevant code excerpt; do not fabricate or alter it.
```

- **Recommended Fix:**

```python
# Minimal illustrative remediation adapted to the project.
```

- **Why This Helps:** [Explain the protection and any remaining limitations]

## 4. Not Verified

- [List important questions that static source review could not answer, or write "None identified."]

## 5. Prioritized Next Steps

1. [Most important action]
2. [Next action]
3. [Optional hardening or validation]

## 6. Review Limitations

State that this was a read-only source-code review.

List files or runtime behavior that were not available.

Do not imply that the application was executed, that a real camera was accessed, or that an external upload was tested.
