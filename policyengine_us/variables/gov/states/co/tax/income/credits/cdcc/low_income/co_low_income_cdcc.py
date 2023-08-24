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

        # Get sum of all qualified child care expenses, class "childcare_expenses" is based on SPMunit
        # Better choice to use class "tax_unit_childcare_expenses", which based on Taxunit and then distribute to SPMunit
        # reference: class nyc_cdcc_age_restricted_expenses(Variable)
        children = tax_unit("tax_unit_children", period)
        # Check child's age is under 13 and check class is_child -- under tax_unit
        person = tax_unit.members
        eligible_child = person("age", period) < p.child_age_threshold
        eligible_children = tax_unit.sum(eligible_child)
        tax_unit_childcare_expenses = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        # avoid divide-by-zero warnings by not using where() function
        eligible_child_ratio = np.zeros_like(children)
        mask = children > 0
        eligible_child_ratio[mask] = eligible_children[mask] / children[mask]
        total_expenses = tax_unit_childcare_expenses * eligible_child_ratio
        # The childcare expenses can not exceed the earned income of the filer
        # if filing jointly - the lesser of either individual's earned income
        earned_income = tax_unit("min_head_spouse_earned", period)
        capped_expenses = min_(earned_income, total_expenses)
        co_low_income_cdcc = capped_expenses * p.rate
        # Credit is capped at $500 or $1,000 for 1 or over 2 dependents, respectively.
        max_amount = p.max_amount.calc(eligible_children)
        return min_(co_low_income_cdcc, max_amount)
