from policyengine_us.model_api import *


class ma_eaedc_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-440"
    )
    
    def formula(spm_unit, period, parameters):
        