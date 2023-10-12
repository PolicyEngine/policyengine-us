from policyengine_us.model_api import *


class disqualified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Disqualified income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/32#:~:text=In%20the%20case%20of%20an,exceed%20the%20earned%20income%20amount"
    definition_period = YEAR
    adds = "gov.irs.gross_income.disqualified_income"
