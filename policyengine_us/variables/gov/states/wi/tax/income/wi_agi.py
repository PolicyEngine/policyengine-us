from policyengine_us.model_api import *


class wi_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin Adjusted Gross Income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf"
    )
    defined_for = StateCode.WI
    adds = ["adjusted_gross_income", "wi_additions"]
    subtracts = ["wi_income_subtractions"]
