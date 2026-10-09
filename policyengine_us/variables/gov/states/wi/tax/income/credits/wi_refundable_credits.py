from policyengine_us.model_api import *


class wi_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin refundable credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/d",
        "https://docs.legis.wisconsin.gov/2025/related/acts/174.pdf#page=2",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        standard = add(tax_unit, period, p.refundable)
        permitted = add(tax_unit, period, p.retirement_income_exclusion_refundable)
        elected = tax_unit("wi_retirement_income_exclusion_elected", period)
        return where(elected, permitted, standard)
