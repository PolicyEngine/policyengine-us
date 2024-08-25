from policyengine_us.model_api import *


class ma_eaedc_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Age eligible for Massachusetts EAEDC "
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-600"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc
        person = spm_unit.members
        age = person("age", period)

        return spm_unit.any(age >= p.age_threshold)  # & ~ ssi_eligible
