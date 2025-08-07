from policyengine_us.model_api import *


class ma_tcap_gross_unearned_income(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Transitional Cash Assistance Program (TCAP) gross unearned income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-210"
    )
    defined_for = StateCode.MA

    adds = "gov.states.ma.dta.tcap.gross_income.unearned"
