from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)

# Fees drop their cents. Income reaches the fee in float32, so a fee that should
# come to whole dollars can fall a hair short of them; this tolerance keeps such
# a fee from losing a dollar.
WHOLE_DOLLAR_TOLERANCE = 0.001


def drop_cents(amount):
    return np.floor(amount + WHOLE_DOLLAR_TOLERANCE)


class co_ccap_parent_fee(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program parent fee"
    documentation = (
        "One monthly fee for the household, in whole dollars: the base fee "
        "plus the fee for additional children, at 55% when every child in "
        "care is in part-time care, and 20% lower when a provider rates in "
        "the top three quality levels. Each step drops the cents, as the "
        "Department's parent fee tool does."
    )
    reference = (
        # PDF pages 79, 81-85
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=79",
        "https://drive.google.com/file/d/1HtPiC2qxclzWfBa7LRo2Uohrg-RCBkyZ/view",
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(spm_unit, period, parameters):
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap
        base_fee = spm_unit("co_ccap_base_parent_fee", period)
        add_on_fee = spm_unit("co_ccap_add_on_parent_fee", period)
        full_time_fee = drop_cents(base_fee + add_on_fee)

        person = spm_unit.members
        in_care = person("co_ccap_child_in_care", period)
        part_time = person("co_ccap_child_in_part_time_care", period)
        children_in_care = spm_unit("co_ccap_children_in_care", period)
        all_part_time = (children_in_care > 0) & (
            spm_unit.sum(in_care & ~part_time) == 0
        )
        fee = where(
            all_part_time,
            drop_cents(full_time_fee * p.parent_fee.part_time.rate),
            full_time_fee,
        )

        # One provider in the top three quality levels is enough.
        rating = person("co_quality_rating_of_child_care_facility", period.this_year)
        highest_rating = spm_unit.max(rating * in_care)
        quality_factor = p.is_quality_rating_discounted.calc(highest_rating)
        return where(children_in_care > 0, drop_cents(fee * quality_factor), 0)
