from policyengine_us.model_api import *

# splitmix64 finalizer (Steele, Lea and Flood, 2014): a fixed, vectorized
# integer hash. Python's hash() is salted per process, and person_id % 12 is
# not uniform on survey IDs such as CPS PH_SEQ * 100 + P_SEQ.
SPLITMIX64_SHIFTS = (np.uint64(30), np.uint64(27), np.uint64(31))
SPLITMIX64_MULTIPLIERS = (
    np.uint64(0xBF58476D1CE4E5B9),
    np.uint64(0x94D049BB133111EB),
)


def unemployment_compensation_start_month_index(person_id):
    """Map person IDs to a calendar-month index (0 = January) by hashing."""
    first_shift, second_shift, third_shift = SPLITMIX64_SHIFTS
    first_multiplier, second_multiplier = SPLITMIX64_MULTIPLIERS
    x = np.asarray(person_id).astype(np.uint64)
    x = (x ^ (x >> first_shift)) * first_multiplier
    x = (x ^ (x >> second_shift)) * second_multiplier
    x = x ^ (x >> third_shift)
    return (x % np.uint64(MONTHS_IN_YEAR)).astype(int)


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
        "that wraps within the year. The block starts in a month drawn from a "
        "deterministic hash of person_id (the splitmix64 finalizer, modulo "
        "12), so each calendar month carries about one twelfth of "
        "unemployment compensation person-months across microdata; person_id "
        "0, the first person in a household situation, starts in January and "
        "person_id 1 in February. A person with 12 months (including anyone "
        "with unemployment compensation but no weeks unemployed) receives in "
        "every month. Known limitations: the block is an allocation device, "
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
        person_id = person("person_id", period.this_year)
        start = unemployment_compensation_start_month_index(person_id)
        position = (period.start.month - 1 - start) % MONTHS_IN_YEAR
        return position < months
