from policyengine_us.model_api import *


class ok_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK
    adds = ["ok_income_tax_before_refundable_credits", "ok_use_tax"]
    subtracts = ["ok_refundable_credits"]
