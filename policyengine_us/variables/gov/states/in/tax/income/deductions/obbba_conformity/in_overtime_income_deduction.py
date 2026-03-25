from policyengine_us.model_api import *


class in_overtime_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana overtime income deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://iga.in.gov/pdf-documents/124/2026/senate/bills/SB0243/SB0243.05.ENRH.pdf#page=52",
        "https://iga.in.gov/legislative/2026/bills/senate/243",
    )
    defined_for = StateCode.IN
    adds = ["overtime_income_deduction"]
