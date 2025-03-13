from policyengine_us.model_api import *


class ma_eaedc_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income of each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210"
    )

    adds = "gov.states.ma.dta.tcap.eaedc.income.sources.earned"
