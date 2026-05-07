from policyengine_us.model_api import *


class wa_birth_to_three_eceap_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Income-eligible for Washington Birth to Three ECEAP"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = "https://app.leg.wa.gov/RCW/default.aspx?cite=43.216.578"

    def formula(person, period, parameters):
        # Birth to Three uses its own FPG/SMI toggle: 130% FPL until
        # 2026-07-01, then 50% SMI. Standard ECEAP transitions on 2025-07-01,
        # so we cannot share the parent toggle.
        p = parameters(period).gov.states.wa.dcyf.eceap.birth_to_three_eceap
        spm_unit = person.spm_unit
        income = spm_unit("wa_eceap_family_income", period)
        if p.uses_fpg:
            threshold = spm_unit("spm_unit_fpg", period) * p.income.fpg_rate
        else:
            threshold = spm_unit("hhs_smi", period) * p.income.smi_rate
        return income <= threshold
