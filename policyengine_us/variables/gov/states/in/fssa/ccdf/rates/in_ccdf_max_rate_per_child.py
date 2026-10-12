from policyengine_us.model_api import *


class in_ccdf_max_rate_per_child(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Indiana CCDF maximum monthly reimbursement rate per child"
    definition_period = MONTH
    defined_for = "in_ccdf_eligible_child"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=37"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states["in"].fssa.ccdf.rates
        provider_type = person("in_ccdf_provider_type", period)
        ptq_level = person("in_ccdf_ptq_level", period)
        age_group = person("in_ccdf_age_group", period)
        weekly_rate = p.full_time[provider_type][ptq_level][age_group]
        monthly_rate = weekly_rate * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        # Per the Policy Manual, the subsidy may exceed the reimbursement rate
        # by 10% for children with documented special needs.
        special_needs_multiplier = where(
            person("is_disabled", period.this_year),
            p.special_needs_multiplier,
            1,
        )
        return monthly_rate * special_needs_multiplier
