from policyengine_us.model_api import *


class wi_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin deduction for contributions to 529 plans"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.edvest.com/learn/tax-benefits/",
        "https://dfi.wi.gov/Pages/EducationalServices/CollegeSavingsCareerPlanning/CollegeSavingsProgram.aspx",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.subtractions.plan_529
        contributions = tax_unit("investment_in_529_plan", period)
        filing_status = tax_unit("filing_status", period)
        beneficiaries = add(
            tax_unit,
            period,
            ["count_529_contribution_beneficiaries"],
        )
        cap = p.cap[filing_status] * beneficiaries
        return min_(contributions, cap)
