from policyengine_us.model_api import *


class mi_interest_dividends_capital_gains_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan interest, dividends, and capital gains deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.deductions.interest_dividends_capital_gains.income_types"
