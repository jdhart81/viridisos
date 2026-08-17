# Security policy

Do not open a public issue for credentials, private keys, personal data,
certificate-forgery paths, or an unpatched remote vulnerability. Use GitHub's
private vulnerability reporting for the public ViridisOS repository. Until
that repository exists, use the private business contact already published by
Viridis and include **ViridisOS security** in the subject.

Include the affected version/commit, minimal reproduction, impact, and any
known mitigation. Do not access data or systems beyond what is necessary to
demonstrate the issue.

## Current trust boundary

The reference runtime is not the production Viridis trust root. Default HMAC
and development signers are test fixtures; their output is self-rooted and must
not be represented as an authoritative "Certified by ViridisOS" certificate.
Production signing keys, mark authorization, revocation, settlement rails, and
customer systems are outside the open payload.

Supported security fixes target the latest release. Verification-only use must
remain free and must not require a secret.
