"""Check canonical citation metadata and sibling keys core can ignore.

Core copies metadata on parameters, dated values, scales and nodes without
moving sibling ``reference`` or ``unit`` keys into it. Where an allowed-key
list is supplied, its unknown-key warning exempts those legacy siblings.
YAML-defined nodes have no allowed-key list: a ``unit`` key can become a child
or raise a parsing error. Nodes skip YAML children and files named
``reference``, but still load directories with that name. The 14 citations
beside dated values in gov/irs/income/exemption/amount.yaml were lost until
#9609 moved them under ``metadata``.

Citation aliases such as ``metadata.references`` remain under their supplied
names instead of populating canonical ``metadata.reference``. Core does not
warn about unknown metadata keys, so the raw scan checks the two known citation
misspellings while leaving other metadata opaque.

Core emits ``ParameterKeyWarning`` for unknown siblings only where it validates
an allowed-key list. ``policyengine_us.model_api`` ignores warnings, so the last
test reloads the parameter tree with that warning recorded. These tests do not
change core's legacy loader compatibility.
"""

from pathlib import Path
import warnings

import policyengine_core.warnings as core_warnings
import pytest
import yaml
from policyengine_core.parameters import Parameter, ParameterNode

REPO = Path(__file__).resolve().parents[2]
PARAMETER_DIRS = (REPO / "parameters", REPO / "params_on_demand")
# Repository placement convention; core's legacy exemptions do not migrate keys.
METADATA_ONLY_KEYS = {"reference", "unit"}
MISSPELLED_METADATA_REFERENCE_KEYS = {"references", "refrence"}
Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def keys_outside_metadata(text, keys=METADATA_ONLY_KEYS):
    """Return (line, key path) for misplaced keys and known citation aliases.

    Metadata is opaque except for direct citation misspellings and YAML merges
    supplying metadata entries. Canonical citation payloads and other metadata
    values are not traversed.
    """
    found = []

    def walk(node, path, in_metadata=False):
        if isinstance(node, yaml.MappingNode):
            for key_node, value_node in node.value:
                key = key_node.value
                key_path = [*path, str(key)]
                if in_metadata:
                    if key in MISSPELLED_METADATA_REFERENCE_KEYS:
                        found.append((key_node.start_mark.line + 1, ".".join(key_path)))
                    if key_node.tag == "tag:yaml.org,2002:merge":
                        walk(value_node, key_path, in_metadata=True)
                    continue
                if key == "metadata":
                    if isinstance(value_node, yaml.MappingNode):
                        walk(value_node, key_path, in_metadata=True)
                    continue
                if key in keys:
                    found.append((key_node.start_mark.line + 1, ".".join(key_path)))
                walk(value_node, key_path)
        elif isinstance(node, yaml.SequenceNode):
            for index, item in enumerate(node.value):
                walk(item, [*path, str(index)], in_metadata=in_metadata)

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


@pytest.mark.parametrize("misspelling", sorted(MISSPELLED_METADATA_REFERENCE_KEYS))
@pytest.mark.parametrize(
    "text, line, key_path",
    [
        (
            "values:\n"
            "  2020-01-01: 1\n"
            "metadata:\n"
            "  {misspelling}: https://a.gov/parameter.pdf\n",
            4,
            "metadata.{misspelling}",
        ),
        (
            "values:\n"
            "  2020-01-01:\n"
            "    value: 1\n"
            "    metadata:\n"
            "      {misspelling}: https://a.gov/value.pdf\n",
            5,
            "values.2020-01-01.metadata.{misspelling}",
        ),
        (
            "brackets:\n"
            "  - threshold:\n"
            "      2020-01-01: 0\n"
            "    metadata:\n"
            "      {misspelling}: https://a.gov/bracket.pdf\n",
            5,
            "brackets.0.metadata.{misspelling}",
        ),
        (
            "metadata:\n  <<:\n    {misspelling}: https://a.gov/merged.pdf\n",
            3,
            "metadata.<<.{misspelling}",
        ),
        (
            "metadata:\n"
            "  defaults: &citations\n"
            "    {misspelling}: https://a.gov/alias.pdf\n"
            "  <<: *citations\n",
            3,
            "metadata.<<.{misspelling}",
        ),
        (
            "metadata:\n"
            "  defaults: &citations\n"
            "    {misspelling}: https://a.gov/alias-list.pdf\n"
            "  other: &other\n"
            "    label: Example\n"
            "  <<: [*other, *citations]\n",
            3,
            "metadata.<<.1.{misspelling}",
        ),
    ],
)
def test_metadata_citation_misspellings_are_found(misspelling, text, line, key_path):
    assert keys_outside_metadata(text.format(misspelling=misspelling)) == [
        (line, key_path.format(misspelling=misspelling))
    ]


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
        "metadata:\n"
        "  custom:\n"
        "    references: Arbitrary nested metadata\n"
        "    refrence: Also opaque\n"
        "    metadata:\n"
        "      references: Still nested inside an arbitrary field\n",
        "metadata:\n"
        '  "<<":\n'
        "    references: A quoted literal key is not a YAML merge\n"
        "    refrence: Also opaque\n",
        "metadata:\n"
        "  reference:\n"
        "    - title: Citation\n"
        "      href: https://a.gov/citation.pdf\n"
        "      references: Citation payloads are opaque\n",
        "metadata:\n"
        "  defaults: &defaults\n"
        "    unit: currency-USD\n"
        "    reference: https://a.gov/merged.pdf\n"
        "  <<: *defaults\n",
        "metadata:\n"
        "  defaults: &defaults\n"
        "    unit: currency-USD\n"
        "  citations: &citations\n"
        "    reference: https://a.gov/merged-list.pdf\n"
        "  <<: [*defaults, *citations]\n",
    ],
)
def test_keys_inside_metadata_are_accepted(text):
    assert keys_outside_metadata(text) == []


@pytest.mark.parametrize("misspelling", sorted(MISSPELLED_METADATA_REFERENCE_KEYS))
def test_correcting_metadata_citation_alias_preserves_value(misspelling):
    text = (
        "values:\n"
        "  '2020-01-01':\n"
        "    value: 1\n"
        "metadata:\n"
        f"  {misspelling}:\n"
        "    - title: Example law\n"
        "      href: https://a.gov/law\n"
    )
    corrected_text = text.replace(f"  {misspelling}:", "  reference:")
    original = Parameter("example", data=yaml.load(text, Loader=Loader))
    corrected = Parameter("example", data=yaml.load(corrected_text, Loader=Loader))
    citations = [{"title": "Example law", "href": "https://a.gov/law"}]

    assert original.values_list[0].value == corrected.values_list[0].value == 1
    assert "reference" not in original.metadata
    assert original.metadata[misspelling] == citations
    assert corrected.metadata["reference"] == citations
    assert misspelling not in corrected.metadata
    assert keys_outside_metadata(text) == [(5, f"metadata.{misspelling}")]
    assert keys_outside_metadata(corrected_text) == []


def parameter_files(directories=PARAMETER_DIRS):
    for directory in directories:
        for suffix in (".yaml", ".yml"):
            yield from sorted(
                path for path in directory.rglob(f"*{suffix}") if path.is_file()
            )


def test_parameter_files_include_both_yaml_extensions(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    expected = {tmp_path / "parameter.yaml", nested / "parameter.yml"}
    for path in expected:
        path.write_text("values:\n  2020-01-01: 1\n")
    (tmp_path / "README.md").write_text("Not a parameter file.\n")

    assert set(parameter_files((tmp_path,))) == expected


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
        "Parameter citation/unit keys must use canonical metadata placement. "
        "Move sibling reference/unit keys under metadata, and rename direct "
        "metadata.references or metadata.refrence keys to metadata.reference:\n"
        + "\n".join(errors)
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
