from policyengine_us.model_api import *


class net_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "net investment income (NII) that is base of the NII Tax (NIIT)"
    reference = "https://www.law.cornell.edu/uscode/text/26/1411"
    unit = USD

    adds = "gov.irs.investment.income.sources"
