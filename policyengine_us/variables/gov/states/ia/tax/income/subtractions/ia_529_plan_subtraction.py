from policyengine_us.model_api import *


class ia_529_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa subtraction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legis.iowa.gov/docs/code/422.7.pdf",
        "https://www.isave529.com/save/tax-benefits",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap * beneficiaries
        return min_(contributions, cap)
