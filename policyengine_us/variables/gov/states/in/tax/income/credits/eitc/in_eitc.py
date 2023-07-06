from policyengine_us.model_api import *


class in_eitc(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Indiana EIC"
    unit = "currency-USD"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible_children = tax_unit.sum(person("is_child_eligible_eitc", period))
        p = parameters(period).gov.states["in"].tax.income.credits.eitc
        eitc = tax_unit("earned_income_tax_credit", period) # needs to be > 0
        earned_income = tax_unit("employment_income", period) # needs to be less than parameter
        federal_agi = tax_unit("adjusted_gross_income", period) # needs to be less than parameter

        earned_eligible = p.child_income_bracket_eligibility.calc(eligible_children) < earned_income 
        agi_eligible = p.child_income_bracket_eligibility.calc(eligible_children) < federal_agi
        eligible = earned_eligible & agi_eligible

        return eligible * (eitc * p.match)