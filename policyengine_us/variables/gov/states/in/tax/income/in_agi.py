from policyengine_us.model_api import *


class in_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"
    )
    defined_for = StateCode.IN

    adds = ["adjusted_gross_income", "in_add_backs"]
    subtracts = ["in_deductions", "in_exemptions"]
