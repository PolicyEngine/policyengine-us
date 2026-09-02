from collections import defaultdict

from policyengine_core.parameters import Parameter, ParameterNode

from policyengine_us.system import system


def _nearest_breakdown_with_unit(parameter):
    ancestor = parameter.parent
    while ancestor is not None:
        if isinstance(ancestor, ParameterNode):
            metadata = ancestor.metadata or {}
            if metadata.get("breakdown") and metadata.get("unit") is not None:
                return ancestor
        ancestor = ancestor.parent
    return None


def test_breakdown_metadata_reaches_value_bearing_children():
    violations = defaultdict(list)

    for parameter in system.parameters.get_descendants():
        if not isinstance(parameter, Parameter):
            continue

        breakdown = _nearest_breakdown_with_unit(parameter)
        if breakdown is None:
            continue

        expected_unit = breakdown.metadata["unit"]
        expected_period = breakdown.metadata.get("period")
        actual_unit = parameter.metadata.get("unit")
        actual_period = parameter.metadata.get("period")
        if actual_unit != expected_unit or (
            expected_period is not None and actual_period != expected_period
        ):
            violations[breakdown.name].append(parameter.name)

    summaries = []
    for breakdown_name, parameter_names in sorted(violations.items()):
        examples = ", ".join(parameter_names[:3])
        if len(parameter_names) > 3:
            examples += ", ..."
        summaries.append(
            f"{breakdown_name}: {len(parameter_names)} children ({examples})"
        )

    assert not violations, (
        "Breakdown parameter units and periods must reach their "
        "value-bearing children. Add `propagate_metadata_to_children: true` "
        "to the parent metadata, or define matching metadata on every child.\n"
        + "\n".join(summaries)
    )
