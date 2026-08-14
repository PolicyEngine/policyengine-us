from policyengine_us.model_api import *


class WYCCAPDayLength(Enum):
    PART_DAY = "Part day (under 5 hours)"
    FULL_DAY = "Full day (5 or more hours)"


class wy_ccap_day_length(Variable):
    value_type = Enum
    entity = Person
    possible_values = WYCCAPDayLength
    default_value = WYCCAPDayLength.FULL_DAY
    definition_period = MONTH
    defined_for = StateCode.WY
    label = "Wyoming CCAP day length"
    reference = (
        "https://dfs.wyo.gov/services/family-services/child-care/",  # Wyoming DFS Table I - Child Care Sliding Fee Scale, eff. 04/01/25-03/31/26 (single page)
        "https://dfs.wyo.gov/about/policy-manuals/child-care-subsidy-policy-manual/",  # Wyoming DFS Child Care Subsidy Policy Manual §1101.N.1 (PDF p. 2)
    )

    def formula(person, period, parameters):
        # Table I / Manual §1101.N.1: a part day is less than five hours of
        # care and a full day is five or more hours.
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        p = parameters(period).gov.states.wy.dfs.ccap.rates
        is_full_day = hours_per_day >= p.day_length_min_hours
        return where(
            is_full_day,
            WYCCAPDayLength.FULL_DAY,
            WYCCAPDayLength.PART_DAY,
        )
