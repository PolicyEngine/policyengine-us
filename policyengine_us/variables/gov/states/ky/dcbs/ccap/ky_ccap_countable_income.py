from policyengine_us.model_api import *


class ky_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=7"

    adds = "gov.states.ky.dcbs.ccap.income.countable_income.sources"
