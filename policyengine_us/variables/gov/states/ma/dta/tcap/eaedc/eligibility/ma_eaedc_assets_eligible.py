from policyengine_us.model_api import *


class ma_eaedc_assets_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Assets eligible for the Massachusetts EAEDC"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-110"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.assets
        countable_assets = add(spm_unit, period, ["ma_eaedc_assets"])

        return countable_assets <= p.limit
