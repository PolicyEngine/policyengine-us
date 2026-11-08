"""A small, contract-compliant slice of the shipped population.

Two microsimulations over the whole default dataset do not fit a CI runner, and
``subsample`` rebuilds the entire dataset as one wide frame before it shrinks
it. Slice whole households out of the shipped file instead: the result keeps the
observed county inputs and the source-backed SPM independence roles that the
input contract requires, which the legacy policyengine-us-data CPS files do not
carry.
"""

from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.system import DEFAULT_DATASET, _resolve_dataset_path


GROUP_ENTITIES = ("tax_unit", "spm_unit", "family", "marital_unit")


def default_population_sample(households: int = 500) -> USSingleYearDataset:
    """Return the first ``households`` whole households of the default build."""
    source = USSingleYearDataset(file_path=_resolve_dataset_path(DEFAULT_DATASET))
    kept = set(source.household["household_id"].iloc[:households])
    person = source.person[source.person["person_household_id"].isin(kept)]
    tables = {
        "person": person,
        "household": source.household[source.household["household_id"].isin(kept)],
    }
    for entity in GROUP_ENTITIES:
        frame = getattr(source, entity)
        identifiers = set(person[f"person_{entity}_id"])
        tables[entity] = frame[frame[f"{entity}_id"].isin(identifiers)]
        # A partially sliced group entity would misstate its own composition.
        members = source.person[source.person[f"person_{entity}_id"].isin(identifiers)]
        assert len(members) == len(person), (
            f"{entity} spans households outside the slice; widen the slice"
        )
    return USSingleYearDataset(
        time_period=int(source.time_period),
        **{name: frame.reset_index(drop=True) for name, frame in tables.items()},
    )
