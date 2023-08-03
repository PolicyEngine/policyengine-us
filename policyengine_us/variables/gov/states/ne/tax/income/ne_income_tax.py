from policyengine_us.model_api import *


class ne_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.NE
    adds = ["ne_income_tax_before_refundable_credits"]
    subtracts = ["ne_refundable_credits"]
