from policyengine_us.model_api import *


class az_529_college_savings_plans_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona 529 college savings plans subtraction"
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
        person = tax_unit.members
        beneficiary = add(
            tax_unit, period, ["college_savigns_plan_529_benefitiary"]
        )
        max_sub = cap * beneficiary

        return min_(contributions_529, max_sub)
