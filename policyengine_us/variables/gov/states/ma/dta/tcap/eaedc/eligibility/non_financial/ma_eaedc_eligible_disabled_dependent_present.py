from policyengine_us.model_api import *


class ma_eaedc_eligible_disabled_dependent_present(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Disabled dependent present for Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-340"
    )

    def formula(spm_unit, period, parameters):
        # Check if household has disabled dependents
        person = spm_unit.members
        is_disabled = person("is_disabled", period)
        is_dependent = person("is_tax_unit_dependent", period)
        disabled_dependent = is_disabled & is_dependent
        disabled_dependent_present = spm_unit.any(disabled_dependent)

        # If there are disabled dependents, check if at least one meets income eligibility
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.income
        earned_income = person("ma_tcap_gross_earned_income", period)

        # A disabled dependent is income eligible if their income is below the limit
        disabled_dependent_income_eligible = disabled_dependent & (
            earned_income < p.disabled_limit
        )

        # The household is eligible if there's at least one income-eligible disabled dependent
        return disabled_dependent_present & spm_unit.any(
            disabled_dependent_income_eligible
        )
