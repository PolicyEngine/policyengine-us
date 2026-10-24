from policyengine_us.model_api import *


class ri_retirement_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island retirement income subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-II/44-30-12.htm"
    )
    defined_for = "ri_retirement_income_subtraction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
        person = tax_unit.members
        retirement_income = add(person, period, p.sources)
        # Military pensions deducted under the separate military subtraction
        # cannot also use the general pension exclusion. Other survivor
        # annuities remain eligible for the general age and income rules.
        military_subtraction = person("ri_military_retirement_subtraction", period)
        retirement_income = max_(retirement_income - military_subtraction, 0)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Cap applies per person, not per tax unit
        capped_per_person = min_(retirement_income, p.cap) * head_or_spouse
        return tax_unit.sum(capped_per_person)
