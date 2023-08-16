from policyengine_us.model_api import *


class co_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Low-income Child Care Expenses Credit"
    unit = USD
    documentation = "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitions"
    definition_period = YEAR
    defined_for = "co_low_income_cdcc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.credits.cdcc.low_income
        # The childcare expenses can not exceed the earned income of the filer
        # if filing jointly - the lesser of either individual's earned income
        earned_income = tax_unit("min_head_spouse_earned", period)
        # Get sum of all qualified child care expenses
        spm_unit = tax_unit.spm_unit
        spm_unit_cdcc_expense = spm_unit("childcare_expenses", period)

        # Distribute the SPM unit's cdcc evenly across children in SPM unit's Tax units
        # reference: class tax_unit_childcare_expenses(Variable)
        spm_unit_count_children = add(spm_unit, period, ["is_child"])
        tax_unit_count_children = add(tax_unit, period, ["is_child"])
        child_ratio = np.zeros_like(spm_unit_count_children)
        mask = spm_unit_count_children > 0
        child_ratio[mask] = (
            tax_unit_count_children[mask] / spm_unit_count_children[mask]
        )
        tax_unit_cdcc_expense = spm_unit_cdcc_expense * child_ratio

        # Check child's age is under 13 and check class is_child -- under tax_unit
        person = tax_unit.members
        age = person("age", period)
        eligible_child = age < p.child_age_threshold

        eligible_expenses = eligible_child * tax_unit_cdcc_expense
        total_expenses = tax_unit.sum(eligible_expenses)
        capped_expenses = min_(earned_income, total_expenses)
        co_low_income_cdcc = capped_expenses * p.rate
        # Credit is capped at $500 or $1,000 for 1 or over 2 dependents, respectively.
        eligible_children = tax_unit.sum(eligible_child)
        max_amount = p.max_amount.calc(eligible_children)
        return min_(co_low_income_cdcc, max_amount)
