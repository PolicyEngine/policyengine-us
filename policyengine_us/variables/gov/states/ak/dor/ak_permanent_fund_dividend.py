from policyengine_us.model_api import *


class ak_permanent_fund_dividend(Variable):
    value_type = float
    entity = Person
    label = "Alaska Permanent Fund Dividend"
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = StateCode.AK

    adds = ["gov.states.ak.dor.permanent_fund_dividend"]
