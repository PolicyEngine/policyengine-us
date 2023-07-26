from policyengine_us.model_api import *


class wi_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=31"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=31"
    )
    defined_for = StateCode.WI
    adds = ["wi_income_tax_before_refundable_credits"]
    subtracts = ["wi_refundable_credits"]
