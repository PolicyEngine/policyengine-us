from policyengine_us.model_api import *


class wi_childcare_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin childcare expense credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Wisconsin matches the potential federal credit
        us_cdcc = tax_unit("cdcc_potential", period)
        p = parameters(period).gov.states.wi.tax.income
        return us_cdcc * p.credits.childcare_expense.fraction
