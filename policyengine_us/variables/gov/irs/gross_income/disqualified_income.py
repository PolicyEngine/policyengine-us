from policyengine_us.model_api import *


class earned_income_disqualified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Earned Income Disqualified income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/32"
    definition_period = YEAR
    adds = "gov.irs.gross_income.disqualified_income"
