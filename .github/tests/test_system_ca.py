"""Exercise the CI trust-store guard using actual public root certificates."""

import importlib.util
import ssl
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "verify_system_ca", ROOT / ".github/actions/setup-system-ca/verify.py"
)
verify_system_ca = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_system_ca)
FIXTURES = Path(__file__).parent / "fixtures/tls"


class SystemCATests(unittest.TestCase):
    def test_unaffected_root_remains_usable(self):
        verify_system_ca.verify_ca_bundle(FIXTURES / "emsign-g1.pem")

    def test_compromised_chains_are_rejected_even_in_a_mixed_bundle(self):
        with TemporaryDirectory() as temporary:
            bundle = Path(temporary) / "ca-certificates.crt"
            for filename, name in (
                ("emsign-ecc-g3.pem", "emSign ECC Root CA - G3"),
                ("aaa-certificate-services.pem", "AAA Certificate Services"),
            ):
                with self.subTest(root=name):
                    bundle.write_text(
                        (FIXTURES / "emsign-g1.pem").read_text()
                        + (FIXTURES / filename).read_text()
                    )
                    with self.assertRaisesRegex(ValueError, name):
                        verify_system_ca.verify_ca_bundle(bundle)

    def test_missing_or_invalid_bundle_fails_closed(self):
        with TemporaryDirectory() as temporary:
            bundle = Path(temporary) / "ca-certificates.crt"
            with self.assertRaises(FileNotFoundError):
                verify_system_ca.verify_ca_bundle(bundle)
            bundle.write_text("This is not a CA certificate bundle.\n")
            with self.assertRaises(ssl.SSLError):
                verify_system_ca.verify_ca_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
