from policyengine_us.model_api import *


class ma_eaedc_disabled_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Disability income eligibility for the Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-340"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        person = spm_unit.members
        disabled_income = person("ma_eaedc_disabled_earned_income", period)
        # All disabled people should have income less than the limit
        return spm_unit.all(disabled_income < p.disabled_limit)
