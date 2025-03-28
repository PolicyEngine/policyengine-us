from policyengine_us.model_api import *


class ma_eaedc_eligible_elderly_present(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible elderly present for the Massachusetts EAEDC"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-600"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.age_threshold
        person = spm_unit.members
        age = person("monthly_age", period)
        is_ssi_eligible = person("is_ssi_eligible", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        elderly = age >= p.elderly

        return spm_unit.any(elderly & is_head_or_spouse & ~is_ssi_eligible)
