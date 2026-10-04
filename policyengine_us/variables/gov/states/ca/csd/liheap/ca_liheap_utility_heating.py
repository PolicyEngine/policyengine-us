from policyengine_us.model_api import *


class ca_liheap_utility_heating(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "California LIHEAP regular gas or electric utility heating benefit"
    defined_for = "ca_liheap_utility_eligible"
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=182,183,184"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.payment
        county = spm_unit.household("county_str", period)
        supported_county = np.isin(county, list(p.utility_base_amount))
        # defined_for masks results after calculation, so replace irrelevant
        # county keys before vectorized lookup in mixed-state populations.
        safe_county = where(supported_county, county, next(iter(p.utility_base_amount)))
        group = max_(spm_unit("ca_liheap_income_group", period), 1)
        base = p.utility_base_amount[safe_county][group]
        size = spm_unit("ca_liheap_household_size", period)
        extra_people = clip(size - 1, 0, p.maximum_payment_household_size - 1)
        return where(
            supported_county, base + p.additional_person_amount * extra_people, 0
        )
