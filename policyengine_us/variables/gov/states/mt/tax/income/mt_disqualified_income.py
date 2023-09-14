from policyengine_us.model_api import *


class mt_disqualified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana disqualified income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = "gov.states.mt.tax.income.credits.ctc.income.disqualified_income"
