from policyengine_us.model_api import *


class al_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama adjusted gross income"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    # The Code of Alabama 1975
    reference = "https://alison.legislature.state.al.us/code-of-alabama"

    adds = "gov.states.al.tax.income.agi.gross_income_sources"
    subtracts = "gov.states.al.tax.income.agi.deductions"
