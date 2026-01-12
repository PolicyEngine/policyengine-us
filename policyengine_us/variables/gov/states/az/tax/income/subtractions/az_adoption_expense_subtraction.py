from policyengine_us.model_api import *


class az_adoption_expense_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adoption expense subtraction"
    unit = USD
    documentation = "https://www.azleg.gov/ars/43/01022.htm"
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.subtractions.adoption

        filing_status = tax_unit("az_filing_status", period)
        person = tax_unit.members
        expenses = tax_unit.sum(
            person("qualified_adoption_assistance_expense", period)
        )

        max_amount = p.max_amount[filing_status]

        return min_(expenses, max_amount)
