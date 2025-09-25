from policyengine_us.model_api import *


class mn_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expense credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = "mn_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.cdcc
        dep_count = tax_unit("mn_cdcc_dependent_count", period)
        # calculate qualifying care expenses
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        # ... cap expense by number of qualifying dependents
        eligible_count = min_(dep_count, p.maximum_dependents)
        maximum_eligible_expenses = min_(
            expenses, p.maximum_expense * eligible_count
        )
        # ... cap expense by lower earnings of head and spouse if present
        # Line 2
        capped_expenses = min_(
            maximum_eligible_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
        # calculate pre-phaseout credit amount
        # Line 5
        agi = tax_unit("adjusted_gross_income", period)
        # Line 7
        pre_phaseout_amount = capped_expenses * p.expense_fraction.calc(agi)
        # calculate post-phaseout credit amount
        # Line 8
        phaseout_amount = tax_unit("mn_cdcc_phase_out", period)
        smaller_of_expenses_and_reduced_credit = min_(
            pre_phaseout_amount, phaseout_amount
        )
        return where(
            agi > p.phaseout_threshold,
            smaller_of_expenses_and_reduced_credit,
            pre_phaseout_amount,
        )
