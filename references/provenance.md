# Implementation provenance

The Android SDK parsers and subprocess adapter were extracted from the
project-owned AppCopy `freeze-android-target-artifacts` implementation.
The standalone export workflow, verifier, and tests are maintained here.

Original source SHA-256: `96ae994710d2ed4fcbb47517cb175ff23a41d81ac7083d9f45278508455d19e4`.

This package does not import AppCopy, invoke its analyzer, or emit an AppCopy
TargetArtifactSet certification. Its `android-apk-export` manifest describes
installed APK acquisition only.
