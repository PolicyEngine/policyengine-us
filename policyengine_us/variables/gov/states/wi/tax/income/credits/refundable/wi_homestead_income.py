from policyengine_us.model_api import *


class wi_homestead_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin homestead credit income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=27"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=3"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=28"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        return 0
