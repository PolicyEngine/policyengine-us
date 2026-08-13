from policyengine_us.model_api import *


class tn_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee CCAP countable monthly income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/Income%20Eligibility%20Limits%20and%20CoPay%20Chart%2010.1.25.pdf#page=1"

    adds = "gov.states.tn.dhs.ccap.income.countable_income.sources"
