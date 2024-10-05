from policyengine_us.model_api import *


class ok_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        itax_before_credits = tax_unit("ok_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("ok_nonrefundable_credits", period)
        return max_(0, itax_before_credits - nonrefundable_credits)
