from collections import defaultdict

from policyengine_core.parameters import Parameter, ParameterNode

from policyengine_us.system import system


METADATA_PROPAGATION_EXCLUSIONS = {
    # Propagating this container's metadata would also activate its currently
    # unapplied uprating rule. Remove after policyengine-core#537 provides a
    # deny-list for metadata propagation.
    ("gov.usda.snap.asset_test.limit", "unit"),
    ("gov.usda.snap.asset_test.limit", "period"),
}


def _nearest_ancestor_with_metadata(parameter, metadata_key):
    ancestor = parameter.parent
    while ancestor is not None:
        if isinstance(ancestor, ParameterNode):
            metadata = ancestor.metadata or {}
            if metadata.get(metadata_key) is not None:
                return ancestor
        ancestor = ancestor.parent
    return None


def test_container_metadata_reaches_value_bearing_children():
    violations = defaultdict(list)

    for parameter in system.parameters.get_descendants():
        if not isinstance(parameter, Parameter):
            continue

        for metadata_key in ("unit", "period"):
            container = _nearest_ancestor_with_metadata(parameter, metadata_key)
            if container is None:
                continue
            if (container.name, metadata_key) in METADATA_PROPAGATION_EXCLUSIONS:
                continue
            expected = container.metadata[metadata_key]
            actual = parameter.metadata.get(metadata_key)
            if actual != expected:
                violations[container.name].append(
                    f"{parameter.name} ({metadata_key}: {actual!r}, expected {expected!r})"
                )

    summaries = []
    for container_name, parameter_names in sorted(violations.items()):
        examples = ", ".join(parameter_names[:3])
        if len(parameter_names) > 3:
            examples += ", ..."
        summaries.append(
            f"{container_name}: {len(parameter_names)} children ({examples})"
        )

    assert not violations, (
        "Container parameter units and periods must reach their value-bearing "
        "children. Add `propagate_metadata_to_children: true` to the parent "
        "metadata, or define matching metadata on every child.\n" + "\n".join(summaries)
    )
