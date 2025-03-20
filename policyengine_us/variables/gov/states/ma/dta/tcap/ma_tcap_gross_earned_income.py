from policyengine_us.model_api import *


class ma_tcap_gross_earned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) gross earned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210"
    )
    defined_for = StateCode.MA

    adds = "gov.states.ma.dta.tafdc.gross_income.earned"
