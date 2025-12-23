from policyengine_us.model_api import *


class co_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program Countable Income"
    reference = "https://regulations.justia.com/states/colorado/1400/1403/rule-8-ccr-1403-1/applicant-rights/section-8-ccr-1403-1-3-111/"
    unit = USD

    adds = "gov.states.co.ccap.income.countable_sources"
