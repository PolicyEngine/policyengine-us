from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
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
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.copay.board
        income = spm_unit("tx_ccs_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period)
        # TWC sets each Board Contract Year's income ranges from the SMI that
        # takes effect on October 1, so read the SMI at this month.
        monthly_smi = smi(size, state, period, parameters) / MONTHS_IN_YEAR
        children = spm_unit.sum(spm_unit.members("tx_ccs_eligible_child", period))
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
        return copay
