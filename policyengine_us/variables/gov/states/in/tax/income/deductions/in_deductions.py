from policyengine_us.model_api import *


class in_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana deductions"
    unit = USD
    definition_period = YEAR
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3"
    defined_for = StateCode.IN

    adds = "gov.states.in.tax.income.deductions.deductions"
