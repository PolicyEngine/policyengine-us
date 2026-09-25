from policyengine_us.model_api import *


class is_subject_to_snap_abawd(Variable):
    value_type = bool
    entity = Person
    label = "Person is subject to the SNAP ABAWD time limit"
    definition_period = MONTH
    documentation = (
        "Whether the person is subject to the Able-Bodied Adult Without "
        "Dependents (ABAWD) time limit: an able-bodied adult without "
        "dependents (no household member under the dependent-age threshold; "
        "7 CFR 273.24(c)(4) supplies the household-wide framing and "
        "7 U.S.C. 2015(o)(3)(C), as amended by P.L. 119-21, the post-HR1 "
        "under-14 threshold) who is not otherwise exempt "
        "(is_snap_abawd_exempt). This is a status test independent of "
        "compliance: a person who satisfies the requirement through the "
        "20-hour work activity test is still subject to it. A person "
        "working 30 or more hours weekly is not subject, however: they are "
        "exempt from work registration under 7 CFR 273.7(b)(1)(vii) and "
        "therefore exempt from the time limit under 7 U.S.C. 2015(o)(3)(D). "
        "Used by the Medicaid community engagement pass-through, which "
        "excludes people subject to a SNAP work requirement (general or "
        "ABAWD)."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.24",
        "https://www.law.cornell.edu/uscode/text/7/2015#o",
    )

    def formula(person, period, parameters):
        is_exempt = person("is_snap_abawd_exempt", period)
        # "Without dependents" applicability: a person residing with any
        # household member under the dependent-age threshold is not subject
        # to the ABAWD time limit.
        has_household_child = person("has_snap_abawd_household_child", period)
        return ~has_household_child & ~is_exempt
