from policyengine_us.model_api import *


class in_eic(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Indiana EIC"
    unit = USD
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        eligible_children = tax_unit.sum(person("in_eic_eligible_child", period))
        p = parameters(period).gov.states["in"].tax.income.credits.eic
        eitc = tax_unit("earned_income_tax_credit", period) # needs to be > 0
        earned_income = person("earned_income", period) # needs to be less than parameter
        total_earned_income = tax_unit.sum(earned_income)
        federal_agi = tax_unit("adjusted_gross_income", period) # needs to be less than parameter

        earned_eligible = (p.income_threshold.calc(eligible_children)) > total_earned_income 
        agi_eligible = p.income_threshold.calc(eligible_children) > federal_agi
        eligible = earned_eligible & agi_eligible        


        return eligible * (eitc * p.match)