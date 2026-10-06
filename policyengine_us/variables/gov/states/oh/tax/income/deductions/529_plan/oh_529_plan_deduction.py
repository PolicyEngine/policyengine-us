from policyengine_us.model_api import *


class oh_529_plan_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio deduction for contributions to 529 plans"
    unit = USD
    documentation = (
        "The head and spouse deduct their combined contributions for each "
        "beneficiary, plus contributions carried forward for that beneficiary, "
        "up to the limit per beneficiary. Beneficiaries in the tax unit are "
        "limited one by one (investment_in_529_plan_as_beneficiary). The "
        "filers' other contributions went to beneficiaries outside the tax "
        "unit, which the model cannot tell apart: it limits them to the cap "
        "times the number of those beneficiaries, as if split evenly, and does "
        "not model their carryforwards."
    )
    definition_period = YEAR
    reference = (
        # R.C. 5747.70(A): "limited to four thousand dollars for each
        # beneficiary", combined for a taxpayer and spouse "regardless of
        # whether [they] file separate returns or a joint return".
        "https://codes.ohio.gov/assets/laws/revised-code/authenticated/57/5747/5747.70/4-3-2023/5747.70-4-3-2023.pdf#page=1",
        # 2025 IT 1040 instructions, Schedule of Adjustments line 37.
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=25",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.deductions.plan_529_contributions
        person = tax_unit.members
        # Beneficiaries in the tax unit: this year's contributions by the head
        # and spouse plus the excess carried forward, up to the cap each.
        for_member = person("investment_in_529_plan_as_beneficiary", period)
        carryforward = person("oh_529_plan_deduction_carryforward", period)
        member_deduction = tax_unit.sum(min_(for_member + carryforward, p.cap))
        # The head's and spouse's other contributions went to beneficiaries
        # outside the tax unit: those they counted, less the members already
        # given contributions above.
        contributions = tax_unit("investment_in_529_plan", period)
        other_contributions = max_(contributions - tax_unit.sum(for_member), 0)
        other_beneficiaries = max_(
            tax_unit("tax_unit_count_529_contribution_beneficiaries", period)
            - tax_unit.sum(for_member > 0),
            0,
        )
        other_deduction = min_(other_contributions, p.cap * other_beneficiaries)
        return member_deduction + other_deduction
