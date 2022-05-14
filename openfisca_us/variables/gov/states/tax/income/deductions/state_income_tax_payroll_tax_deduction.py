from openfisca_us.model_api import *


class state_income_tax_payroll_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax payroll tax deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        TAXES = [
            "employee_social_security_tax",
            "employee_medicare_tax",
            "self_employment_tax",
        ]
        taxes = add(person, period, TAXES)
        state = person.household("state_code_str", period)
        cap = parameters(period).states.tax.income.deductions.payroll_tax[
            state
        ]
        capped_payroll_tax = min_(taxes, cap)
        eligible_capped_payroll_tax = ~dependent * capped_payroll_tax
        return tax_unit.sum(eligible_capped_payroll_tax)
