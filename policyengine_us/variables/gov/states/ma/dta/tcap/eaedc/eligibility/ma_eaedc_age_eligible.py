from policyengine_us.model_api import *


class ma_eaedc_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Age eligible for the Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-600"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc
        person = spm_unit.members
        age = person("age", period)
        is_ssi_eligible = person("is_ssi_eligible", period)
        elderly = age >= p.age_threshold

        return spm_unit.any(elderly & ~is_ssi_eligible)
