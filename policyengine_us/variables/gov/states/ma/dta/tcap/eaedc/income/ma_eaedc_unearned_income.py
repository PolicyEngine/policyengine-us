from policyengine_us.model_api import *


class ma_eaedc_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210"
    )

    adds = "gov.states.ma.dta.tcap.eaedc.income.sources.unearned"
