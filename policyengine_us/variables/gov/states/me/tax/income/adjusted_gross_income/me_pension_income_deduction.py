from policyengine_us.model_api import *


class me_pension_income_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine pension income deduction"
    unit = USD
    documentation = "Maine pension income deduction, which subtracts from federal AGI to compute Maine AGI."
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members

        # Get the non-militariy pension income of each person (Pension Income Deduction Worksheet, Line 1).
        pension_income = person("pension_income", period)

        # Get the deduction cap (Pension Income Deduction Worksheet, Line 2)
        deduction_cap = parameters(
            period
        ).gov.states.me.tax.income.agi.subtractions.pension_exclusion.cap

        # Get the total social security for each person (Pension Income Deduction Worksheet, Line 3)
        gross_ss = person("social_security", period)

        # Subtract Line 3 from Line 2 to get new cap (line 4).
        ss_reduced_cap = max_(deduction_cap - gross_ss, 0)

        # Get the pension income deduction (line 5).
        pension_income_deduction = min_(pension_income, ss_reduced_cap)

        # Get the military retirement pay (line 6).
        military_retirement_pay = person("military_retirement_pay", period)

        # Get the total deduction.
        deduction = pension_income_deduction + military_retirement_pay

        # Return the total deduction for the tax unit.
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        filing_status = tax_unit("filing_status", period)
        is_joint = filing_status == filing_status.possible_values.JOINT
        return where(
            is_joint,
            tax_unit.sum(where(is_head | is_spouse, deduction, 0)),
            tax_unit.sum(where(is_head, deduction, 0)),
        )
