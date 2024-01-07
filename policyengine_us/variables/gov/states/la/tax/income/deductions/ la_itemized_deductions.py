from policyengine_us.model_api import *


class la_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf",
        "https://www.legis.la.gov/Legis/Law.aspx?d=101760",  # (3)
    ]
    defined_for = StateCode.LA
