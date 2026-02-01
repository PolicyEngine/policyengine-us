from policyengine_us.model_api import *


class ma_tafdc_lump_sum_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC lump sum income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts"
        "/106-CMR-704-250"
    )
    defined_for = StateCode.MA
