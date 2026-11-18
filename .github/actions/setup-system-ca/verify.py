"""Reject Linux CA bundles that still trust the compromised eMudhra chains."""

import hashlib
import ssl
from pathlib import Path


# Root fingerprints published at https://emudhra.we-have-a-problem.com/roots.json.
BLOCKED_ROOTS = {
    "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b": (
        "emSign ECC Root CA - G3"
    ),
    "d7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4": (
        "AAA Certificate Services"
    ),
}


def verify_ca_bundle(path: Path) -> None:
    # An explicit bundle avoids inheriting a Python-specific CA override.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=str(path))
    blocked = {
        BLOCKED_ROOTS[fingerprint]
        for certificate in context.get_ca_certs(binary_form=True)
        if (fingerprint := hashlib.sha256(certificate).hexdigest()) in BLOCKED_ROOTS
    }
    if blocked:
        raise ValueError(f"System CA bundle still trusts: {', '.join(sorted(blocked))}")


if __name__ == "__main__":
    verify_ca_bundle(Path("/etc/ssl/certs/ca-certificates.crt"))
    print("System CA bundle rejects the compromised eMudhra trust roots")
