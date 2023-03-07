from policyengine_us.model_api import *


class tx_tanf_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF income limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.hhs.texas.gov/services/financial/cash/tanf-cash-help"
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.tx.tanf
        return p.monthly_income_limit.calc(size) * MONTHS_IN_YEAR
