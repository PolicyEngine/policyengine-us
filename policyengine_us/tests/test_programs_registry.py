"""Structural guards for the program registry (programs.yaml).

The registry is served through the /us/metadata API as ``modelled_policies``
and renders the model coverage page, so every model reference in it has to
point at something the model defines. Two failure modes have shipped before:
1. A ``variable`` that the model does not define (DC LIHEAP listed
   ``dc_liheap``, but the benefit variable is ``dc_liheap_payment``).
2. A ``parameter_prefix`` that resolves to no parameter node (Riverside County
   LIHEAP listed ``gov.local.ca.riv.liheap``; its parameters live under
   ``gov.local.ca.riv.cap.liheap``).
"""

from collections import Counter
from pathlib import Path

import pytest
import yaml

REGISTRY = Path(__file__).parent.parent / "programs.yaml"

STATUSES = {"complete", "partial", "in_progress"}

# References that did not resolve when this guard was added, keyed by
# (entry label, field). Fix the registry entry and delete its key here; do
# not add new keys.
KNOWN_UNRESOLVED = {
    ("csfp", "variable"),
    ("fdpir", "parameter_prefix"),
    ("social_security", "parameter_prefix"),
    ("clean_vehicle_credits", "variable"),
    ("dc_power", "parameter_prefix"),
    ("dc_gac", "parameter_prefix"),
    ("la_expectant_parent", "parameter_prefix"),
    ("sf_wftc", "variable"),
    ("montgomery_county_eitc", "variable"),
    ("montgomery_county_eitc", "parameter_prefix"),
}


def registry_entries():
    """(label, state or None, entry) for every program and state implementation.

    A state implementation's label includes its name, since a program can list
    more than one implementation for a state (Washington's two ECEAPs).
    """
    programs = yaml.safe_load(REGISTRY.read_text())["programs"]
    entries = []
    for program in programs:
        entries.append((program["id"], None, program))
        for implementation in program.get("state_implementations") or []:
            state = implementation["state"]
            label = f"{program['id']}/{state}/{implementation['name']}"
            entries.append((label, state, implementation))
    return entries


ENTRIES = registry_entries()
ENTRIES_BY_LABEL = {label: entry for label, _, entry in ENTRIES}


def references(field):
    return [
        pytest.param(label, entry[field], id=label)
        for label, _, entry in ENTRIES
        if field in entry
    ]


@pytest.fixture(scope="module")
def system():
    from policyengine_us.system import system

    return system


def parameter_prefix_resolves(system, prefix):
    try:
        system.parameters.get_child(prefix)
    except ValueError:
        return False
    return True


def test_entry_labels_are_unique():
    counts = Counter(label for label, _, _ in ENTRIES)
    duplicates = sorted(label for label, count in counts.items() if count > 1)
    assert not duplicates, f"Duplicate program ids or implementations: {duplicates}"


@pytest.mark.parametrize(
    "label, entry",
    [pytest.param(label, entry, id=label) for label, _, entry in ENTRIES],
)
def test_status_is_known(label, entry):
    assert entry["status"] in STATUSES, (
        f"{label} has status {entry['status']!r}; the registry uses "
        f"{sorted(STATUSES)}. List a program only once work on it has started."
    )


def test_state_implementations_name_valid_states():
    from policyengine_us.variables.household.demographic.geographic.state_code import (
        StateCode,
    )

    valid = {state.value for state in StateCode}
    invalid = sorted(
        label for label, state, _ in ENTRIES if state is not None and state not in valid
    )
    assert not invalid, f"Unknown state codes: {invalid}"


@pytest.mark.parametrize("label, variable", references("variable"))
def test_variable_is_defined(system, label, variable):
    if (label, "variable") in KNOWN_UNRESOLVED:
        pytest.skip("listed in KNOWN_UNRESOLVED")
    assert variable in system.variables, (
        f"{label} names variable {variable!r}, which the model does not define."
    )


@pytest.mark.parametrize("label, prefix", references("parameter_prefix"))
def test_parameter_prefix_resolves(system, label, prefix):
    if (label, "parameter_prefix") in KNOWN_UNRESOLVED:
        pytest.skip("listed in KNOWN_UNRESOLVED")
    assert parameter_prefix_resolves(system, prefix), (
        f"{label} names parameter_prefix {prefix!r}, which resolves to no "
        "parameter node."
    )


def test_known_unresolved_references_are_still_unresolved(system):
    """Keep the exemption list from outliving the bugs it records."""
    stale = []
    for label, field in sorted(KNOWN_UNRESOLVED):
        entry = ENTRIES_BY_LABEL.get(label)
        if entry is None or field not in entry:
            stale.append((label, field))
        elif field == "variable" and entry[field] in system.variables:
            stale.append((label, field))
        elif field == "parameter_prefix" and parameter_prefix_resolves(
            system, entry[field]
        ):
            stale.append((label, field))
    assert not stale, (
        "These KNOWN_UNRESOLVED keys now resolve or no longer exist; "
        f"delete them: {stale}"
    )
