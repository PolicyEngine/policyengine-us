from policyengine_us.model_api import *
from policyengine_us.tools.ny_ccap import ny_ccap_monthly_rate


class ny_ccap_day_care_center_rate(Variable):
    value_type = float
    entity = Person
    label = "New York CCAP monthly day care center payment limit"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "Prices the child's schedule at the day care center market rate that "
        "applies to the child. A child who qualifies for the special-needs "
        "market rate gets that rate here too. 24-OCFS-LCM-22 caps legally "
        "exempt group payments at this amount, including enhancements and "
        "differentials."
    )
    reference = (
        # PDF pages 7, 9
        "https://ocfs.ny.gov/main/policies/external/2024/lcm/24-OCFS-LCM-22.pdf#page=7",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.rates
        county_group = person.household("ny_ccap_county_group", period.this_year)
        age_group = person("ny_ccap_age_group", period.this_year)
        center_rate = ny_ccap_monthly_rate(
            person,
            period,
            parameters,
            p.weekly[county_group]["DCC_SACC"][age_group],
            p.daily[county_group]["DCC_SACC"][age_group],
            p.part_day[county_group]["DCC_SACC"][age_group],
        )
        # LCM-22 makes the special-needs rate the market rate for a
        # qualifying child, so the center rate that caps group payments
        # rises with it.
        special_needs = person("ny_ccap_special_needs_rate_eligible", period)
        return center_rate * where(special_needs, p.special_needs_multiplier, 1)
