from policyengine_us.model_api import *


class mi_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Michigan CDC benefit amount"
    definition_period = MONTH
    defined_for = "mi_ccap_eligible"
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/706.pdf#page=2"
    )

    def formula(spm_unit, period, parameters):
        # BEM 706: the subsidy is a provider reimbursement computed per
        # two-week pay period, capped at the provider's charge per child, less
        # the family contribution, floored at zero, then converted to a monthly
        # amount. There are 26 two-week pay periods per year.
        pay_periods_per_month = WEEKS_IN_YEAR / 2 / MONTHS_IN_YEAR

        person = spm_unit.members
        is_eligible_child = person("mi_ccap_eligible_child", period)
        # Per-child reimbursement per pay period, converted to monthly.
        block_payment = person("mi_ccap_block_payment", period)
        monthly_payment = block_payment * pay_periods_per_month
        # Cap each child's reimbursement at that child's actual monthly charge.
        # pre_subsidy_childcare_expenses is annual; accessing it with the bare
        # monthly period auto-divides it to a monthly amount.
        monthly_expense = person("pre_subsidy_childcare_expenses", period)
        capped_payment = min_(monthly_payment, monthly_expense)
        total_payment = spm_unit.sum(capped_payment * is_eligible_child)

        family_contribution = spm_unit("mi_ccap_family_contribution", period)
        monthly_family_contribution = family_contribution * pay_periods_per_month
        return max_(total_payment - monthly_family_contribution, 0)
