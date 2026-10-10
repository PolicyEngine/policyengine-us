from policyengine_us.model_api import *


class medicaid_ltss_excluded_impairment_related_work_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS claimant-qualified impairment-related work expenses"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Derives the impairment-related work expenses available for an "
        "ordinary Delaware earned-income budget. The person must meet "
        "the disability criteria without blindness and either be under "
        "65 or have received qualifying disability payments for the "
        "month before age 65 (20 CFR 416.1112(c)(6)). Expenses are capped "
        "at this person's work income remaining outside a qualified "
        "income trust. Individual and couple budgets further cap the "
        "deduction at earnings left after the $20 and $65 exclusions; "
        "expenses cannot reduce unearned income. Disability, blindness, "
        "and age use the existing annual facts."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78#page=6",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm",
    )

    def formula_2026_01_01(person, period, parameters):
        disabled = person("meets_ssi_disability_criteria", period.this_year)
        blind = person("is_blind", period.this_year)
        under_65 = person("age", period.this_year) < 65
        qualifying_prior_receipt = person(
            "medicaid_ltss_received_disability_payments_before_age_65", period
        )
        eligible = disabled & ~blind & (under_65 | qualifying_prior_receipt)
        expenses = max_(
            person("medicaid_ltss_impairment_related_work_expenses", period), 0
        )
        earned = person("medicaid_ltss_qit_adjusted_earned_income", period)
        return where(eligible, min_(expenses, earned), 0)
