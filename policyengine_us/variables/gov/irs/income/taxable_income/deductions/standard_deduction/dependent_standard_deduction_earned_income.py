from policyengine_us.model_api import *


class dependent_standard_deduction_earned_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Earned income for the standard deduction worksheet for dependents"
    unit = USD
    documentation = (
        "The filers' earned income as the Standard Deduction Worksheet for "
        "Dependents defines it: taxable wages (after pre-tax payroll "
        "deductions), self-employment income and farm income, less the "
        "deductible part of self-employment tax, and not below zero."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/63#c_5",
        # Standard Deduction Worksheet for Dependents, earned income note:
        # Form 1040 line 1z and Schedule 1 lines 3, 6, 8r, 8t and 8u, less
        # Schedule 1 line 15.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=35",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        # Form 1040 line 1z carries taxable wages (W-2 box 1, after elective
        # deferrals); Schedule 1 lines 3 and 6 carry business and farm
        # income. earned_income has gross wages and leaves out farm income.
        earned = add(
            person,
            period,
            [
                "irs_employment_income",
                "self_employment_income",
                "sstb_self_employment_income",
                "farm_operations_income",
            ],
        )
        return max_(
            tax_unit.sum(filer * earned) - tax_unit("self_employment_tax_ald", period),
            0,
        )
