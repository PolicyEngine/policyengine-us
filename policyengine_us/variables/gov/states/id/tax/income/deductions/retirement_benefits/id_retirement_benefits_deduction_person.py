from policyengine_us.model_api import *


class id_retirement_benefits_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Idaho retirement benefits deduction for each person"
    unit = USD
    documentation = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/"
    definition_period = YEAR
    defined_for = "id_retirement_benefits_deduction_eligible_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits

        # Social Security benefits received amount
        ss_amt = person("taxable_social_security", period)
        # Base amount minus social Security benefits received amount
        ded_amt = max_(max_amt - total_ss_amt, 0)
        # Qualified retirement benefits included in federal income
        relevant_income = add(person, period, p.income_sources)
        eligible_relevant_income = relevant_income * eligible_person
        total_relevant_income = tax_unit.sum(eligible_relevant_income)
        # The smaller one
        return min_(ded_amt, total_relevant_income)
