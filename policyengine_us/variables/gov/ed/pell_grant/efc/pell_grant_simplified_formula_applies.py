from policyengine_us.model_api import *


class pell_grant_simplified_formula_applies(Variable):
    value_type = bool
    entity = Person
    label = "Use Pell Grant simplified formula"
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        head_income = tax_unit("pell_grant_primary_income", period)
        p = parameters(period).gov.ed.pell_grant.efc.simplified
        income_eligible = head_income < p.income_limit
        total_benefits = add(tax_unit, period, p.benefits)
        has_benefits = np.any(total_benefits > 0)
        return income_eligible & has_benefits & p.applies
