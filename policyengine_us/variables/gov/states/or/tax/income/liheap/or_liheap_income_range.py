from policyengine_us.model_api import *


class OregonLIHEAPIncomeRange(Enum):
    RANGE_ONE = "Range one"
    RANGE_TWO = "Range two"
    RANGE_THREE = "Range three"
    RANGE_FOUR = "Range four"


class or_liheap_income_range(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = OregonLIHEAPIncomeRange
    default_value = OregonLIHEAPIncomeRange.RANGE_FOUR
    label = "Income range for Oregon LIHEAP eligibility"
    definition_period = YEAR
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2021-Energy-Assistance-Manual.pdf#page=55"

    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        income = spm_unit("adjusted_gross_income", period)
        threshold = spm_unit("or_liheap_income_threshold", period)
        p = parameters(period).gov.states["or"].liheap

        range1 = threshold * p.range_one
        range2 = threshold * p.range_two
        range3 = threshold * p.range_three

        return select(
            [
                income <= range1,
                income <= range2,
                income <= range3,
            ],
            [
                OregonLIHEAPIncomeRange.RANGE_ONE,
                OregonLIHEAPIncomeRange.RANGE_TWO,
                OregonLIHEAPIncomeRange.RANGE_THREE,
            ],
            default=OregonLIHEAPIncomeRange.RANGE_FOUR,
        )
