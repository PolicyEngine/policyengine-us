from policyengine_us.model_api import *


class ms_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP annual income limit"
    defined_for = StateCode.MS
    reference = (
        # Rule 6.1 C (page 22) and the Appendix 60% State Median Income table
        # (page 58).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=58",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        federal = parameters(period).gov.hhs.smi
        # The published FY2026 limits truncate the four-person 60% SMI amount
        # first, then the household-adjusted amount. This reproduces all 20 rows;
        # it is a reconciled numerical pattern, not an explicit rounding rule.
        four_person_limit = np.floor(federal.amount[state] * p.income_limit)
        adjustment = federal.household_size_adjustment
        threshold = federal.additional_person_threshold
        size_share = (
            adjustment.first_person
            + adjustment.second_to_sixth_person * clip(size - 1, 0, threshold - 1)
            + adjustment.additional_person * max_(size - threshold, 0)
        )
        return where(size > 0, np.floor(four_person_limit * size_share), 0)
