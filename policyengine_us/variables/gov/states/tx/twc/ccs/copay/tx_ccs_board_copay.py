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


def board_scale_amount(scale, income, limit):
    # Each bracket covers income more than its threshold's monthly limit and
    # not more than the next threshold's.
    amount = np.zeros_like(income)
    for threshold, bracket_amount in zip(scale.thresholds, scale.amounts):
        if np.isneginf(threshold):
            in_bracket = np.ones_like(income, dtype=bool)
        else:
            in_bracket = income > limit(threshold)
        amount = where(in_bracket, bracket_amount, amount)
    return amount


def smi_range_limit(monthly_smi):
    # TWC publishes these limits as whole-dollar monthly incomes, the SMI
    # share rounded to the nearest dollar (WD 24-23 Attachment 2; WD 20-24
    # income ranges).
    return lambda share: np.floor(monthly_smi * share + 0.5)


def fpg_range_limit(limits, size):
    # TWC prints these limits by family size, and its table is keyed by the
    # percent of the federal poverty guidelines where each range ends.
    return lambda share: limits[np.full_like(size, round(share * 100))]


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
        smi_limit = smi_range_limit(monthly_smi)
        # TWC's FPG table covers family sizes 2 to 15, so other sizes read the
        # nearest printed size.
        fpg_sizes = [int(key) for key in p.fpg_income_limits]
        fpg_size = clip(size, min(fpg_sizes), max(fpg_sizes))
        fpg_limit = fpg_range_limit(p.fpg_income_limits[fpg_size], fpg_size)
        person = spm_unit.members
        # Board charts charge by children in care; like the statewide branch of
        # tx_ccs_copay, the model counts each eligible child as in care.
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
            limit = fpg_limit if p.uses_fpg_ranges[board.name] else smi_limit
            first_child = board_scale_amount(board_p.first_child, income, limit)
            additional_child = board_scale_amount(
                board_p.additional_child, income, limit
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
        share = copay * (1 - reduction)
        # Some Boards' charts print the reduced share of cost rounded to the
        # nearest dollar.
        share = where(
            p.reduction.rounds_to_dollar[region], np.floor(share + 0.5), share
        )
        # Some Boards cap the share of cost at the family's monthly income.
        share = where(p.caps_at_income[region], min_(share, income), share)
        # A Board's lowest range starts at $0, but TWC reads 40 TAC 809.19's bar
        # on a minimum share of cost to mean a family with no countable income
        # pays nothing (CCDF State Plan 2022-2024, section 3.2.4).
        return where(income > 0, share, 0)
