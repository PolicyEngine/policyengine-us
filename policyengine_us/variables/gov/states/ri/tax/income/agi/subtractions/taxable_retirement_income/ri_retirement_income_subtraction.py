from policyengine_us.model_api import *


class ri_retirement_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island retirement income subtraction"
    unit = USD
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
    defined_for = "ri_retirement_income_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        taxable_pension = person("taxable_pension_income", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
        total_taxable_pension = tax_unit.sum(taxable_pension * head_or_spouse)
        return min_(total_taxable_pension, p.cap)
