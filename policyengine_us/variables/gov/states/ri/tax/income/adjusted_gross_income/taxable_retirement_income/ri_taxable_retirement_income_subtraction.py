from policyengine_us.model_api import *


class ri_taxable_retirement_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Taxable retirement income subtraction"
    unit = USD
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
    defined_for = "ri_taxable_retirement_income_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        taxable_pension = tax_unit.members("taxable_pension_income", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.taxable_retirement_income
        pension_limit = p.cap
        return min_(taxable_pension, pension_limit)
