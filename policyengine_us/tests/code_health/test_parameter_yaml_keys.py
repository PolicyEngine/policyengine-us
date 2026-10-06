"""Every key in a parameter YAML file must be one policyengine-core reads.

policyengine-core reads a parameter's ``reference`` and ``unit`` only from a
``metadata`` block: the parameter's, a dated value's or a node's. It also
accepts both keys anywhere else without the unknown-key warning
(``LEGACY_COMPAT_KEYS`` in policyengine_core/parameters/config.py), and a
parameter node skips any child named ``reference``. So a ``reference:``
written at a file's top level, beside ``values:``, beside a dated
``value:`` or on a scale bracket loads without a word and is dropped. That is
how 14 citations in gov/irs/income/exemption/amount.yaml went missing until
#9609 moved them under ``metadata``.

Every other key core does not recognize raises a ``ParameterKeyWarning``, but
``policyengine_us.model_api`` ignores all warnings, so a typo such as
``refrence:`` is dropped just as silently. The last test loads the parameter
tree with that warning recorded.
"""

import warnings

import policyengine_core.warnings as core_warnings
import pytest
import yaml
from policyengine_core.parameters import ParameterNode

from policyengine_us.model_api import REPO

PARAMETER_DIRS = (REPO / "parameters", REPO / "params_on_demand")
# Keys policyengine-core tolerates outside ``metadata`` but never reads there.
DROPPED_OUTSIDE_METADATA = {"reference", "unit"}
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def keys_outside_metadata(text, keys=DROPPED_OUTSIDE_METADATA):
    """Return (line, key path) for each mapping key in ``keys`` that sits
    outside every ``metadata`` block of the YAML document ``text``."""
    found = []

    def walk(node, path):
        if isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                key = key_node.value
                if key == "metadata":
                    continue
                key_path = [*path, str(key)]
                if key in keys:
                    found.append((key_node.start_mark.line + 1, ".".join(key_path)))
                walk(value_node, key_path)
        elif isinstance(node, yaml.SequenceNode):
            for index, item in enumerate(node.value):
                walk(item, [*path, str(index)])

    walk(yaml.compose(text, Loader=Loader), [])
    return found


@pytest.mark.parametrize(
    "text, expected",
    [
        (
            "description: Top level, beside values.\n"
            "values:\n"
            "  2020-01-01: 1\n"
            "reference:\n"
            "  - title: Rev. Proc. 2019-44\n"
            "    href: https://www.irs.gov/pub/irs-drop/rp-19-44.pdf\n",
            [(4, "reference")],
        ),
        (
            "values:\n"
            "  2026-01-01:\n"
            "    value: 1\n"
            "    metadata:\n"
            "      reference: https://a.gov/2026.pdf\n"
            "  2027-01-01:\n"
            "    value: 2\n"
            "    reference: https://a.gov/2027.pdf\n",
            [(8, "values.2027-01-01.reference")],
        ),
        (
            "reference: https://a.gov/node.pdf\nchild:\n  values:\n    2020-01-01: 1\n",
            [(1, "reference")],
        ),
        (
            "brackets:\n"
            "  - threshold:\n"
            "      2020-01-01: 0\n"
            "    rate:\n"
            "      2020-01-01: 0.1\n"
            "    reference: https://a.gov/scale.pdf\n",
            [(6, "brackets.0.reference")],
        ),
        (
            "brackets:\n"
            "  - threshold:\n"
            "      values:\n"
            "        2020-01-01: 0\n"
            "      reference: https://a.gov/threshold.pdf\n",
            [(5, "brackets.0.threshold.reference")],
        ),
        (
            "unit: currency-USD\nvalues:\n  2020-01-01: 1\n",
            [(1, "unit")],
        ),
    ],
)
def test_keys_outside_metadata_are_found(text, expected):
    assert keys_outside_metadata(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "description: Reference under the parameter's metadata.\n"
        "values:\n"
        "  2020-01-01: 1\n"
        "metadata:\n"
        "  unit: currency-USD\n"
        "  reference:\n"
        "    - title: Rev. Proc. 2019-44\n"
        "      href: https://www.irs.gov/pub/irs-drop/rp-19-44.pdf\n",
        "values:\n"
        "  2027-01-01:\n"
        "    value: 2\n"
        "    metadata:\n"
        "      reference: https://a.gov/2027.pdf\n",
        "metadata:\n"
        "  reference: https://a.gov/node.pdf\n"
        "reference_amount:\n"
        "  values:\n"
        "    2020-01-01: 1\n",
        "brackets:\n"
        "  - threshold:\n"
        "      2020-01-01: 0\n"
        "    metadata:\n"
        "      reference: https://a.gov/bracket.pdf\n",
        "2020-01-01: 1\n",
    ],
)
def test_keys_inside_metadata_are_accepted(text):
    assert keys_outside_metadata(text) == []


def parameter_files():
    for directory in PARAMETER_DIRS:
        yield from sorted(directory.rglob("*.yaml"))


def test_parameter_files_are_found():
    files = list(parameter_files())
    assert len(files) > 1_000
    assert REPO / "parameters/gov/irs/income/exemption/amount.yaml" in files


def test_no_reference_or_unit_outside_metadata():
    errors = [
        f"{path.relative_to(REPO.parent)}:{line}: {key_path}"
        for path in parameter_files()
        for line, key_path in keys_outside_metadata(path.read_text())
    ]
    assert not errors, (
        "policyengine-core drops these keys because they sit outside "
        "metadata. Move each under the metadata of its parameter, dated "
        "value or node:\n" + "\n".join(errors)
    )


def test_parameter_files_have_no_keys_core_ignores():
    parameter_key_warning = getattr(core_warnings, "ParameterKeyWarning", None)
    if parameter_key_warning is None:
        pytest.skip("policyengine-core < 3.32 does not flag unknown keys")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", parameter_key_warning)
        for directory in PARAMETER_DIRS:
            ParameterNode("", directory_path=str(directory))
    messages = sorted(
        {
            str(warning.message)
            for warning in caught
            if issubclass(warning.category, parameter_key_warning)
        }
    )
    assert not messages, "\n".join(messages)
