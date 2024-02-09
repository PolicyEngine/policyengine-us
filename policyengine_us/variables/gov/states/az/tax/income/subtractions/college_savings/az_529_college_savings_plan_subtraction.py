from policyengine_us.model_api import *


class az_529_college_savings_plan_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona 529 college savings plan subtraction"
    unit = USD
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2022_140i.pdf#page=15"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.subtractions.college_savings

        filing_status = tax_unit("filing_status", period)
        contributions_529 = tax_unit("investment_in_529_plan", period)

        cap_per_beneficiary = p.cap[filing_status]
        beneficiaries = add(
            tax_unit, period, ["count_529_contribution_beneficiaries"]
        )
        cap = cap_per_beneficiary * beneficiaries

        return min_(contributions_529, cap)
