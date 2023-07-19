from policyengine_us.model_api import *


class wi_earned_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin earned income credit (WI EITC)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=26"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=26"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        inv_income = tax_unit("eitc_relevant_investment_income", period)
        ineligible = inv_income > p.earned_income.investment_income_limit
        us_eitc = tax_unit("earned_income_tax_credit", period)
        child_count = tax_unit("eitc_child_count", period)
        wi_frac = p.earned_income.fraction.calc(child_count)
        return ~ineligible * us_eitc * wi_frac
