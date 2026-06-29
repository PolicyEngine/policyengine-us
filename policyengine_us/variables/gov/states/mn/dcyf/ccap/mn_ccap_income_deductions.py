from policyengine_us.model_api import *


class mn_ccap_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Minnesota CCAP allowable income deductions"
    definition_period = YEAR
    defined_for = StateCode.MN
    reference = ("https://www.revisor.mn.gov/rules/3400.0170/",)
    adds = "gov.states.mn.dcyf.ccap.income.deductions.sources"
