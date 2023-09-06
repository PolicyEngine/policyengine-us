from policyengine_us.model_api import *


class id_retirement_benefits_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho retirement benefits deduction"
    unit = USD
    documentation = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits
        filing_status = tax_unit("filing_status", period)

        eligible_person = person(
            "id_retirement_benefits_eligible_person", period
        )
        # Base retirement benefits deduction amount
        base_amt = p.amount[filing_status]
        # Social Security benefits received amount
        ss_amt = person("social_security_retirement", period) * eligible_person
        total_ss_amt = tax_unit.sum(ss_amt)
        # Base amount minus social Security benefits received amount
        ded_amt = max_(base_amt - total_ss_amt, 0)
        # Qualified retirement benefits included in federal income
        relevant_income = (
            person("taxable_pension_income", period)
            + person("military_retirement_pay", period)
        ) * eligible_person
        total_relevant_income = tax_unit.sum(relevant_income)
        # The smaller one
        return min_(ded_amt, total_relevant_income)
