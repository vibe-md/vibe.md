
# Media Privacy Reference Vulnerabilities & Fixes

This document contains small teaching examples for the `security-media-privacy` skill.

It shows what risky media-handling patterns can look like and what safer implementation approaches may look like.

These examples are **illustrative, not production-ready drop-in code**. Adapt them to the application's framework, threat model, image formats, consent requirements, and retention policy.

A code review must trace the actual data flow. Matching a snippet is not enough to prove a vulnerability or a fix.

All external service URLs below use the reserved `api.example.com` example domain. Do not replace them with a real endpoint when using these snippets as test material.

---

## 1. Camera Frame Uploaded Without Anonymization

### Vulnerable Pattern

The code reads a camera frame and sends it directly to an external service. No anonymization step is visible.

```python
import cv2
import requests

def capture_and_send():
    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    if ret:
        success, encoded = cv2.imencode(".jpg", frame)

        if success:
            requests.post(
                "https://api.example.com/v1/analyze",
                files={
                    "image": (
                        "frame.jpg",
                        encoded.tobytes(),
                        "image/jpeg"
                    )
                }
            )

    cap.release()
```

### Safer Direction

The example below deliberately uses a placeholder `anonymize_faces` function.

A real implementation must connect a suitable face-detection and anonymization method, verify that it handles the application's expected images, and fail safely if protection fails.

It must not silently fall back to uploading the original frame.

```python
import cv2
import requests

def anonymize_faces(frame):
    """
    Replace this placeholder with a tested implementation.

    It must return a protected frame or raise an exception.
    It must not return the original frame when detection
    or anonymization fails.
    """
    raise NotImplementedError(
        "Connect a tested anonymization implementation"
    )


def capture_and_send():
    cap = cv2.VideoCapture(0)

    try:
        ret, frame = cap.read()

        if not ret or frame is None:
            raise RuntimeError(
                "Could not read a camera frame"
            )

        # Never transmit the original frame.
        protected_frame = anonymize_faces(frame)

        success, encoded = cv2.imencode(
            ".jpg",
            protected_frame
        )

        if not success:
            raise RuntimeError(
                "Could not encode the protected frame"
            )

        response = requests.post(
            "https://api.example.com/v1/analyze",
            files={
                "image": (
                    "protected-frame.jpg",
                    encoded.tobytes(),
                    "image/jpeg",
                )
            },
            timeout=10,
        )

        response.raise_for_status()

    finally:
        # Release the camera even if processing or
        # the request fails.
        cap.release()
```

### Audit Notes

- `anonymize_faces` is intentionally unimplemented. The example is not safe to run until a real, tested implementation is supplied.
- A blur function is not automatically sufficient anonymization.
- Check whether all relevant faces and sensitive visual details are covered.
- Check that no other code path logs, saves, caches, or uploads the original frame.
- HTTPS protects the connection in transit. It does not anonymize the image or control the recipient's retention.

---

## 2. Uploaded Image Saved With Its Original EXIF Metadata

### Vulnerable Pattern

Opening an image and saving it without an explicit metadata-removal step may preserve metadata, depending on the library and format.

```python
from PIL import Image

def save_upload(uploaded_file):
    image = Image.open(uploaded_file)

    image.save("uploads/user-photo.jpg")
```

### Safer Direction

For a JPEG output, one approach is to create a fresh RGB image from the oriented pixel data and save that new image without passing the original EXIF data.

```python
from PIL import Image, ImageOps

def save_upload_without_original_exif(uploaded_file):

    with Image.open(uploaded_file) as source:

        # Apply orientation before creating the new image.
        oriented = ImageOps.exif_transpose(source)

        rgb_image = oriented.convert("RGB")

        # Create a fresh image containing pixels,
        # not the original EXIF block.
        clean_image = Image.new(
            "RGB",
            rgb_image.size
        )

        clean_image.paste(rgb_image)

        clean_image.save(
            "uploads/user-photo.jpg",
            format="JPEG"
        )
```

### Audit Notes

- EXIF is metadata stored inside some image files. It can include GPS location, capture time, camera make/model, and other details.
- This example intentionally converts the output to JPEG/RGB. That may change transparency, color information, or other format-specific properties.
- Choose the output format deliberately.
- Verify the actual saved output in tests.
- Do not assume that every image format, library, or export path strips every metadata type.
- Also inspect thumbnails, original-upload archives, object storage, logs, and backups.
- Saving a cleaned copy does not remove an original copy stored elsewhere.

---

## 3. Temporary Media File Not Removed on Every Path

### Vulnerable Pattern

If processing or the network request fails, a temporary file may be left behind.

```python
import cv2
import requests

def upload_frame(frame):

    path = "/tmp/captured-frame.jpg"

    cv2.imwrite(path, frame)

    with open(path, "rb") as image_file:

        requests.post(
            "https://api.example.com/v1/analyze",
            files={"image": image_file}
        )
```

### Safer Direction

Prefer an in-memory encoded buffer when the application does not need a disk file.

```python
import cv2
import requests

def upload_frame(frame):

    success, encoded = cv2.imencode(
        ".jpg",
        frame
    )

    if not success:
        raise RuntimeError(
            "Could not encode frame"
        )

    response = requests.post(
        "https://api.example.com/v1/analyze",
        files={
            "image": (
                "frame.jpg",
                encoded.tobytes(),
                "image/jpeg"
            )
        },
        timeout=10,
    )

    response.raise_for_status()
```

If a temporary disk file is genuinely required:

- Use a unique temporary filename.
- Restrict access as appropriate for the platform.
- Delete it in a `finally` block or with a context manager.
- Avoid fixed shared filenames such as `/tmp/captured-frame.jpg`, which can cause collisions and unintended access.

### Audit Notes

- In-memory buffers and disk files are different storage risks.
- Do not report an in-memory buffer as an unencrypted temporary disk file.
- Deleting a temporary file is useful, but it does not guarantee secure erasure from every filesystem, backup, or storage layer.
- Check all success and error paths, including exceptions and retries.

---

## 4. Suggested Test Scenarios for Developers

These are test ideas for the project owner to implement in their own test environment.

The audit skill itself must not access a live camera, upload real user media, or call an external service.

### Test 1: Anonymization Ordering

Verify that the protected image, not the original frame, is passed to the upload function.

Expected result:

- The upload receives the anonymized frame.
- The original frame is not transmitted.

### Test 2: Anonymization Failure

Simulate a detection or anonymization error.

Expected result:

- The application does not upload the original frame as a fallback.
- The error is handled safely.

### Test 3: Metadata Removal

Save a test image containing known EXIF GPS metadata.

Inspect the output file and verify that the sensitive metadata is absent.

### Test 4: Temporary-File Cleanup

Simulate both successful processing and an exception.

Expected result:

- The temporary file is removed in both cases.

### Test 5: Unexpected Copies

Check whether original images are also written to:

- Application logs.
- Cache directories.
- Debug folders.
- Backups.
- Other storage locations.

Use synthetic or non-sensitive test images.

Keep tests pointed at mocks or local test services, not real external endpoints.

---

## 5. What These Examples Do Not Prove

- A matching vulnerable snippet does not prove that a real project has the same vulnerability.
- A matching remediation snippet does not prove that the real project is protected.
- Static code review cannot always establish runtime behavior, third-party retention, or every metadata behavior.
- Face blurring is not a universal guarantee of anonymity.
- HTTPS does not remove sensitive information from media.
- A successful static audit does not replace application testing.

Always base findings on the actual project code and its data flow.
