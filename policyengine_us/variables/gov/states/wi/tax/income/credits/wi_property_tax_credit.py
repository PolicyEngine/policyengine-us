from policyengine_us.model_api import *


class wi_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=17"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        rent = add(tax_unit, period, ["rent"])
        ptax = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.states.wi.tax.income.credits.property_tax
        proptax = ptax + rent * p.rent_fraction
        return min_(p.max, proptax * p.rate)
