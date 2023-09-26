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
        ).gov.states.az.tax.income.subtractions.529_college_savings_plans

        filing_status = tax_unit("filing_status", period).possible_values

        contributions_529 = tax_unit("investment_in_529_plan", period)
        max_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                p.amount.single,
                p.amount.joint,
                p.amount.head_of_household,
                p.amount.separate,
                p.amount.widow,
            ],
        )
        
        return 
