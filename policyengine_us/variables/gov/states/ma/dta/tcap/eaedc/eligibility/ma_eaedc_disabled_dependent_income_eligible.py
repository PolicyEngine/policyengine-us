from policyengine_us.model_api import *


class ma_eaedc_disabled_dependent_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Disabled dependent person's income eligibility for the Massachusetts EAEDC"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-340"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        disabled_income = person(
            "ma_eaedc_disabled_dependent_earned_income", period
        )
        # All disabled & dependent people should have income less than the limit
        return disabled_income < p.disabled_limit
