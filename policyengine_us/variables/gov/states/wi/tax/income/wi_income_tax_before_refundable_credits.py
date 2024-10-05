from policyengine_us.model_api import *


class wi_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        income_tax_before = tax_unit("wi_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("wi_nonrefundable_credits", period)
        return max_(0, income_tax_before - nonrefundable_credits)
