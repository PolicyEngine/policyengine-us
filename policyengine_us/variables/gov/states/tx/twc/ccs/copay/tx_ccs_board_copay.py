from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_care_schedule import (
    TXCCSCareSchedule,
)
from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_provider_rating import (
    TXCCSProviderRating,
)
from policyengine_us.variables.gov.states.tx.twc.ccs.tx_ccs_workforce_board_region import (
    TXCCSWorkforceBoardRegion,
)


def board_scale_amount(scale, income, monthly_smi):
    # Each bracket covers income more than its threshold share of SMI and not
    # more than the next one. TWC publishes these limits as whole-dollar
    # monthly incomes, the SMI share rounded to the nearest dollar (WD 24-23
    # Attachment 2; WD 20-24 income ranges).
    amount = np.zeros_like(income)
    for threshold, bracket_amount in zip(scale.thresholds, scale.amounts):
        if np.isneginf(threshold):
            in_bracket = np.ones_like(income, dtype=bool)
        else:
            in_bracket = income > np.floor(monthly_smi * threshold + 0.5)
        amount = where(in_bracket, bracket_amount, amount)
    return amount


class tx_ccs_board_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Texas Child Care Services (CCS) copayment under the local Workforce Board scale"
    documentation = "Monthly parent share of cost under the scale each Local Workforce Development Board set before TWC's statewide scale took effect with TX3C."
    definition_period = MONTH
    defined_for = "tx_ccs_eligible"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-19",
        "https://web.archive.org/web/20240908233001/https://www.twc.texas.gov/sites/default/files/wf/policy-letter/wd/wd-24-23-twc.pdf#page=1",
        "https://www.twc.texas.gov/sites/default/files/wf/policy-letter/wd/20-24-twc.pdf#page=1",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/ccdf-state-plan-2022-2024-twc.pdf#page=97",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.copay.board
        income = spm_unit("tx_ccs_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period)
        # TWC sets each Board Contract Year's income ranges from the SMI that
        # takes effect on October 1, so read the SMI at this month.
        monthly_smi = smi(size, state, period, parameters) / MONTHS_IN_YEAR
        person = spm_unit.members
        eligible_child = person("tx_ccs_eligible_child", period)
        children = spm_unit.sum(eligible_child)
        additional_children = max_(children - 1, 0)
        region = spm_unit.household("tx_ccs_workforce_board_region", period)

        copay = np.zeros_like(income)
        for board in TXCCSWorkforceBoardRegion:
            # Only Boards with a sourced scale for this period have one.
            if not p.applies[board.name]:
                continue
            board_p = p[board.name.lower()]
            first_child = board_scale_amount(board_p.first_child, income, monthly_smi)
            additional_child = board_scale_amount(
                board_p.additional_child, income, monthly_smi
            )
            copay = where(
                region == board,
                first_child + additional_child * additional_children,
                copay,
            )

        # Some Boards reduce the share of cost for a child at a Texas Rising
        # Star provider or for a family whose children are all in part-time
        # care. A family that qualifies for both gets the greater reduction.
        rating = person("tx_ccs_provider_rating", period)
        texas_rising_star = (
            (rating == TXCCSProviderRating.TRS2)
            | (rating == TXCCSProviderRating.TRS3)
            | (rating == TXCCSProviderRating.TRS4)
        )
        has_texas_rising_star_child = spm_unit.any(eligible_child & texas_rising_star)
        schedule = person("tx_ccs_care_schedule", period)
        full_time = schedule == TXCCSCareSchedule.FULL_TIME
        all_part_time = spm_unit.sum(eligible_child & full_time) == 0
        reduction = max_(
            has_texas_rising_star_child * p.reduction.texas_rising_star[region],
            all_part_time * p.reduction.part_time[region],
        )
        # A Board's lowest range starts at $0, but TWC reads 40 TAC 809.19's bar
        # on a minimum share of cost to mean a family with no countable income
        # pays nothing (CCDF State Plan 2022-2024, section 3.2.4).
        return where(income > 0, copay * (1 - reduction), 0)
