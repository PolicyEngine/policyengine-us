from policyengine_us.model_api import *


class al_federal_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama federal tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2023/01/22f40abk.pdf#page=20"
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        income_tax = tax_unit("al_income_tax_before_credits", period)
        net_investment_income_tax = tax_unit(
            "net_investment_income_tax", period
        )
        federal_tax = income_tax + net_investment_income_tax
        eitc = tax_unit("eitc", period)
        american_opportunity_credit = tax_unit(
            "american_opportunity_credit", period
        )
        ctc = tax_unit("ctc", period)
        al_credits = eitc + american_opportunity_credit + ctc
        return max_(federal_tax - al_credits, 0)
