from policyengine_us.model_api import *


class de_poc(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Delaware Purchase of Care benefit amount"
    definition_period = MONTH
    defined_for = "de_poc_eligible"
    reference = (
        "https://dhss.delaware.gov/wp-content/uploads/sites/2/dss/pdf/PurchaseofCareProviderHandbook_FINAL1_25_2023.pdf#page=95",
        "https://dhss.delaware.gov/dss/childcr/",
    )

    def formula(spm_unit, period, parameters):
        copay = spm_unit("de_poc_copay", period)
        maximum_weekly_benefit = add(
            spm_unit, period, ["de_poc_maximum_weekly_benefit"]
        )
        maximum_monthly_benefit = maximum_weekly_benefit * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        capped_expenses = min_(pre_subsidy_childcare_expenses, maximum_monthly_benefit)
        ordinary_benefit = max_(capped_expenses - copay, 0)
        person = spm_unit.members
        eligible_child = person("de_poc_eligible_child", period)
        referred = person("de_poc_has_dfs_referral", period) & eligible_child
        has_referred_child = spm_unit.any(referred)
        ordinary_requirements = spm_unit("de_poc_income_eligible", period) & spm_unit(
            "de_poc_activity_eligible", period
        )
        payable = eligible_child & (referred | spm_unit.project(ordinary_requirements))
        # Referral eligibility belongs to the referred child. Siblings still
        # need the ordinary family requirements to contribute to the payment.
        child_expense = person("pre_subsidy_childcare_expenses", period)
        child_maximum = person("de_poc_maximum_weekly_benefit", period) * (
            WEEKS_IN_YEAR / MONTHS_IN_YEAR
        )
        referred_expense = spm_unit.sum(min_(child_expense, child_maximum) * payable)
        return where(
            has_referred_child, max_(referred_expense - copay, 0), ordinary_benefit
        )
