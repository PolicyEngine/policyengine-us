from policyengine_us.model_api import *


class co_low_income_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado Low-income Child Care Expenses Credit"
    unit = USD
    documentation = "https://casetext.com/statute/colorado-revised-statutes/title-39-taxation/specific-taxes/income-tax/article-22-income-tax/part-1-general/section-39-22-1195-child-care-expenses-tax-credit-legislative-declaration-definitions"
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.co.tax.income.credits.cdcc.low_income
        # Filer is eligible if AGI is below $25,000
        agi = tax_unit("adjusted_gross_income", period)
        # The childcare expenses can not exceed the earned income of the filer 
        # if filing jointly - the lesser of either individual's earned income
        earned_income = tax_unit("min_head_spouse_earned", period)
        # Get sum of all qualified child care expenses 
        expenses = person("childcare_expenses", period)     
        age = person("age", period)
        age_eligible = age < p.child_age_limit
        eligible_expenses = age_eligible * expenses
        total_expenses = tax_unit.sum(eligible_expenses)
        capped_expenses = min_(earned_income, total_expenses)
        co_cdcc = capped_expenses * p.rate.calc(agi)
        # Credit is capped at $500 or $1,000 for 1 or over 2 dependents respectfully
        dependents = tax_unit("tax_unit_dependents", period)
        max_amount = p.max_amount.calc(dependents)
        return min_(co_cdcc, max_amount)
