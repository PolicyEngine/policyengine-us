from policyengine_us.model_api import *

STORED_START_MONTH = "unemployment_compensation_start_month"

# Start months (0 = January) for household positions 0 to 11 when a household
# situation supplies no unemployment_compensation_start_month. They are the
# months the model's former hash (the splitmix64 finalizer of the position,
# modulo 12) gave those positions, kept so household results do not change.
# Position 12 and later reuse the list from its start.
SITUATION_START_MONTH_INDEX = np.array([0, 1, 10, 8, 8, 0, 4, 4, 4, 3, 5, 5])

# TRANSITIONAL: datasets built before the start month was stored, among them
# every Populace US release to date, carry no
# unemployment_compensation_start_month. For those datasets alone the start
# month is still hashed from person_id, exactly as before, so their results
# do not change. The hash is deleted, and such a dataset raises instead, once
# the national and ACS local-area releases that pe-us and policyengine.py pin
# both store the column and policyengine.py's input-table adapter declares
# that its populations come from a dataset. Until then
# tests/code_health/test_no_engine_time_randomness.py ratchets this hash and
# every call of legacy_start_month_index.
SPLITMIX64_SHIFTS = (np.uint64(30), np.uint64(27), np.uint64(31))
SPLITMIX64_MULTIPLIERS = (
    np.uint64(0xBF58476D1CE4E5B9),
    np.uint64(0x94D049BB133111EB),
)


def legacy_start_month_index(key):
    """The pre-stored start month (0 = January): splitmix64(key) mod 12."""
    first_shift, second_shift, third_shift = SPLITMIX64_SHIFTS
    first_multiplier, second_multiplier = SPLITMIX64_MULTIPLIERS
    x = np.asarray(key).astype(np.uint64)
    # NOTE: the multiplications wrap modulo 2**64 by design. numpy warns on
    # that overflow only for 0-d (scalar) inputs, so the warning is silenced.
    with np.errstate(over="ignore"):
        x = (x ^ (x >> first_shift)) * first_multiplier
        x = (x ^ (x >> second_shift)) * second_multiplier
    x = x ^ (x >> third_shift)
    return (x % np.uint64(MONTHS_IN_YEAR)).astype(int)


def start_month_supplied(simulation):
    """Whether the simulation holds the start month as an input it can read.

    Presence follows the stored inputs, never the values, so a column of
    zeros counts as supplied. It covers columns a dataset supplies, values set
    after construction and inputs a parent branch holds. A reform that
    neutralizes the start month leaves it unsupplied.
    """
    holder = simulation.get_holder(STORED_START_MONTH)
    return len(holder.get_input_periods(simulation.branch_name)) > 0


def stored_start_month_index(person, stored, period):
    """Start month index (0 = January) of a data-built simulation."""
    if not start_month_supplied(person.simulation):
        person_id = person("person_id", period.this_year)
        return legacy_start_month_index(person_id)
    if not stored.all():
        missing = int((stored == 0).sum())
        raise ValueError(
            f"The dataset supplies {STORED_START_MONTH}, but {missing} of "
            f"{stored.size} people have no start month in {period.this_year}. "
            "The dataset build must assign a start month (1-12) to every "
            "person in every year it covers."
        )
    return stored - 1


def situation_start_month_index(person, stored):
    """Start month index (0 = January) of a household situation."""
    # NOTE: the position counts a household's members in the order the
    # situation lists its people, whatever person_id they carry, and is the
    # same in every axis copy of the household.
    position = person.household.reference_entity.members_position
    default = SITUATION_START_MONTH_INDEX[position % SITUATION_START_MONTH_INDEX.size]
    return where(stored > 0, stored - 1, default)


class is_receiving_unemployment_compensation(Variable):
    value_type = bool
    entity = Person
    label = "Receiving unemployment compensation in the month"
    definition_period = MONTH
    documentation = (
        "Whether the person receives unemployment compensation in the month, "
        "for the SNAP work registration exemption of 7 CFR 273.7(b)(1)(v), "
        "which describes a current status. The unemployment_compensation_months "
        "of the year are placed as one contiguous block of calendar months "
        "that wraps within the year, starting in "
        "unemployment_compensation_start_month. Datasets store that start "
        "month, assigned when the dataset is built; for now a dataset that "
        "stores none keeps the start month the model used to hash from "
        "person_id. A household situation "
        "may supply it; otherwise the start follows the person's position in "
        "their household, which is the same in every axis copy: the first "
        "member starts in January, the second in February, the third in "
        "November and the fourth in September. A person with 12 "
        "months (including anyone with unemployment compensation but no "
        "weeks unemployed) receives in every month. Known limitations: the "
        "block is an allocation device, "
        "not observed timing, so the January value that the Medicaid "
        "community engagement pass-through reads changes for recipients whose "
        "block excludes January; ACS-based rows keep the all-year exemption "
        "until weeks_unemployed is supplied (PolicyEngine/microcosm#1022); and "
        "under 7 CFR 273.7(b)(2)(ii) an exemption lost through a change that "
        "is not subject to reporting lapses only at recertification, so ending "
        "it after the block can be stricter than practice."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_1_v",
        "https://www.law.cornell.edu/cfr/text/7/273.7#b_2",
    )

    def formula(person, period, parameters):
        months = person("unemployment_compensation_months", period.this_year)
        stored = person(STORED_START_MONTH, period.this_year)
        if np.any((stored < 0) | (stored > MONTHS_IN_YEAR)):
            raise ValueError(
                f"{STORED_START_MONTH} must be a calendar month from 1 to 12, "
                "or 0 when not supplied."
            )
        if person.simulation.is_over_dataset:
            start = stored_start_month_index(person, stored, period)
        else:
            start = situation_start_month_index(person, stored)
        position = (period.start.month - 1 - start) % MONTHS_IN_YEAR
        return position < months
