from policyengine_us.model_api import *


class az_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Arizona Child Care Assistance Program countable income"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=28"
    adds = "gov.states.az.hhs.ccap.income.countable_income.sources"
