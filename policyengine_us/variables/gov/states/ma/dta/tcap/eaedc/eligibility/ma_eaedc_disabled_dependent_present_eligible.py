from policyengine_us.model_api import *


class ma_eaedc_disabled_dependent_present_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets the disabled dependent criteria for Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-340"
    )

    def formula(spm_unit, period, parameters):
        # Check if household has disabled dependents
        person = spm_unit.members
        is_disabled = person("is_disabled", period)
        is_dependent = person("is_tax_unit_dependent", period)
        has_disabled_dependent = spm_unit.any(is_disabled & is_dependent)

        # If there are disabled dependents, check if they all meet income eligibility
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        disabled_income = person(
            "ma_eaedc_disabled_dependent_earned_income", period
        )
        disabled_dependent_income_eligible = spm_unit.all(
            disabled_income < p.disabled_limit
        )
        return has_disabled_dependent & disabled_dependent_income_eligible
