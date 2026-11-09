---
name: media-memory-guard
description: Audits code for Computer Vision privacy leaks (unblurred frames, EXIF metadata, streaming risks) and AI long-term memory vulnerabilities (cross-session leaks, context poisoning in Vector DBs).
category: Security
author: Yael Tamari
---

# Media Privacy & AI Memory Guard (`media-memory-guard`)

## Purpose
Enforce privacy and security standards in applications integrating Computer Vision (OpenCV, MediaPipe, YOLO, OpenPose) and AI Long-Term Memory systems (Vector Databases, persistent chat sessions, RAG pipelines).

## When to Use
Run this skill when:
- Reviewing code that captures, streams, or processes camera/image data.
- Reviewing persistent vector database interactions (ChromaDB, Pinecone, PGVector, etc.).
- Performing pre-deployment security audits for Multimodal AI apps.
- The user asks: "Audit media privacy", "Check vector memory isolation", or "Review CV safety".

---

## Instructions & Checkpoints

The agent must perform a non-destructive, evidence-based code review covering the following audit areas:

### Part A: Computer Vision & Media Privacy Audit

1. **Image & Stream Anonymization (Blurring / Masking):**
   - Check if video/camera frames (OpenCV `VideoCapture`, Canvas streams) undergo face or background blurring before storage or cloud API transmission.
   - Flag any raw image frame sent directly to external multimodal APIs without anonymization options.

2. **EXIF & GPS Metadata Leakage:**
   - Verify image uploading code strips EXIF tags (specifically GPS coordinates and camera device identifiers).
   - Flag missing metadata sanitization steps during image ingestion pipelines.

3. **In-Memory Frame Retention & Temporary Storage:**
   - Inspect temporary directories (`/tmp`, unencrypted local disks) for unhashed or unencrypted raw media files.
   - Ensure image buffer objects are cleared or garbage-collected promptly to prevent memory inspection leaks.

---

### Part B: AI Long-Term Memory & Context Isolation

1. **Cross-Session Vector DB Isolation (Tenant Boundaries):**
   - Verify that queries to Vector Databases (Pinecone, ChromaDB, Milvus, PGVector) explicitly include metadata filtering by `user_id` or `session_id`.
   - Flag vector searches (`similarity_search`, `query`) that retrieve context without strict user boundary enforcement.

2. **Persistent Context Poisoning Sanitization:**
   - Audit incoming text before writing to long-term memory (`store_memory`, `insert_vector`).
   - Check for input validation that strips embedded instructions, indirect prompt injections, or malicious system overrides before persistent storage.

---

## Execution Workflow

1. **Scan Workspace:** Identify code files dealing with media ingestion (`cv2`, `PIL`, `webcam`, `ffmpeg`) and memory/vector operations (`langchain`, `llamaindex`, `pinecone`, `chromadb`).
2. **Collect Evidence:** For every vulnerability found, log the exact file path, line numbers, and code snippet.
3. **Severity & Certainty Assessment:** Assign severity (`HIGH`, `MEDIUM`, `LOW`) and certainty confidence (`HIGH`, `MEDIUM`).
4. **Draft Remediation:** Provide a clear, copy-pasteable refactored code block demonstrating how to fix the flaw.

---

## Output Format

Report findings using the following structure:

### 🛡️ Media Privacy & AI Memory Security Report

#### Findings Summary
- **Total Issues Found:** [Number]
- **High Severity:** [Number] | **Medium Severity:** [Number]

---

#### Detailed Findings

##### 🔴 [Issue Title]
- **Category:** [Computer Vision Privacy / Vector Memory Isolation]
- **File:** `path/to/file.ext` (Line XX)
- **Severity:** `HIGH` | **Certainty:** `HIGH`
- **Vulnerability Explanation:** [Clear explanation of why this code poses a risk]
- **Evidence:**
  ```python
  # Problematic code snippet