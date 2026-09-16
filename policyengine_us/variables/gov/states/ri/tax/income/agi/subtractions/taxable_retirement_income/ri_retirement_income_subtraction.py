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
        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
        person = tax_unit.members
        retirement_income = add(person, period, p.sources)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Cap applies per person, not per tax unit
        capped_per_person = min_(retirement_income, p.cap) * head_or_spouse
        return tax_unit.sum(capped_per_person)
