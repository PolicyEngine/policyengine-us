from policyengine_us.model_api import *


class de_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Delaware LIHEAP adjusted annual countable income"
    defined_for = StateCode.DE
    reference = "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=5"

    def formula(spm_unit, period, parameters):
        # Keep income of members excluded from qualified household size.
        # Annual flows approximate the application's assessment period.
        income = add(spm_unit, period, ["de_liheap_countable_income_person", "de_tanf"])
        # This existing annual tax estimate approximates payroll withholding;
        # it does not observe actual withheld tax. It already includes the DE
        # employee paid-leave contribution through employee_payroll_tax.
        deductions = add(
            spm_unit,
            period,
            ["spm_unit_paycheck_withholdings", "de_wilmington_earned_income_tax"],
        )
        # Shared tax estimates can include tax on excluded child/student income.
        # TANF is a household amount with no person-level student allocation.
        return max_(income - max_(deductions, 0), 0)
