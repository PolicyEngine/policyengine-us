from policyengine_us.model_api import *


class co_ccap_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Colorado TANF eligible"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.cccap
        agi = tax_unit("adjusted_gross_income", period)
        fpg = parameters(period).gov.hhs.fpg
        fpg_rate = p.entry_threshold
        spm_unit = tax_unit.spm_unit
        smi = spm_unit("hhs_smi", period)
        smi_rate = p.initial_income_eligibility
        income_eligible = (agi < smi * smi_rate) & (agi < fpg * fpg_rate)

        person = spm_unit.members
         
        disabled = person("is_disabled", period)
        if disabled:
            child_age_eligible = person("age", period) < p.disabled_child_age_limit
        else:
            child_age_eligible = person("age", period) < p.age_limit
        return income_eligible & child_age_eligible

