from policyengine_us.model_api import *


class nd_ccap_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP gross countable income"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"
    adds = "gov.states.nd.dhs.ccap.income.sources"
