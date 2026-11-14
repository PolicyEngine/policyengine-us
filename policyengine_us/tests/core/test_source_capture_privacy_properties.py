"""Check generated capture tokens without constructing a tax-benefit system."""

import base64
import importlib.util
from pathlib import Path

from hypothesis import given, settings, strategies as st


spec = importlib.util.spec_from_file_location(
    "_source_capture_guard",
    Path(__file__).resolve().parents[1] / "code_health" / "test_source_conflicts.py",
)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

CAPTURE_NAME = "source_conflicts/sources/example/capture.html"
TOKEN_PROBLEM = f"{CAPTURE_NAME} contains a base64 UUID-dollar-IPv4 token"


@settings(max_examples=32, deadline=None, database=None, derandomize=True)
@given(
    identifier=st.uuids(),
    last_octet=st.integers(min_value=0, max_value=255),
    padded=st.booleans(),
    uppercase=st.booleans(),
    html=st.booleans(),
)
def test_encoded_visitor_tokens_fail_without_disclosing_values(
    identifier, last_octet, padded, uppercase, html
):
    uuid_text = str(identifier)
    if uppercase:
        uuid_text = uuid_text.upper()
    address = f"203.0.113.{last_octet}"
    decoded = f"{uuid_text}${address}".encode("ascii")
    token = base64.b64encode(decoded)
    if not padded:
        token = token.rstrip(b"=")
    raw = (
        b'<script>const value = "' + token + b'";</script>'
        if html
        else b'"' + token + b'"'
    )

    problems = guard._source_capture_problems(raw, CAPTURE_NAME)

    assert problems == [TOKEN_PROBLEM]
    diagnostic = "\n".join(problems)
    assert token.decode("ascii") not in diagnostic
    assert decoded.decode("ascii") not in diagnostic
    assert address not in diagnostic


@settings(max_examples=32, deadline=None, database=None, derandomize=True)
@given(last_octet=st.integers(min_value=0, max_value=255))
def test_svg_data_and_stylesheet_versions_pass(last_octet):
    address = f"203.0.113.{last_octet}".encode("ascii")
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><text>' + address + b"</text></svg>"
    image = b'<img src="data:image/svg+xml;base64,' + base64.b64encode(svg) + b'">'
    stylesheet = b'<link href="/styles.css?v=' + address + b'">'

    assert guard._source_capture_problems(image, CAPTURE_NAME) == []
    assert guard._source_capture_problems(stylesheet, CAPTURE_NAME) == []
