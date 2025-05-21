from policyengine_us.model_api import *


class OvertimeExemptionCategory(Enum):
    NONE = "No exemption category"
    NEVER_WORKED = "Never worked"
    MILITARY = "Military"
    EXECUTIVE_ADMINISTRATIVE = "Executive, administrative, or professional"
    FARMER_FISHER = "Farmer or fisher"
    COMPUTER_SCIENTIST = "Computer scientist"


class fsla_overtime_occupation_exemption_category(Variable):
    value_type = Enum
    possible_values = OvertimeExemptionCategory
    default_value = OvertimeExemptionCategory.NONE
    entity = Person
    label = "FSLA occupation categories for overtime exemption"
    reference = "https://www.law.cornell.edu/uscode/text/29/213"
    definition_period = YEAR

    def formula(person, period, parameters):
        # Using select with conditions and values for vectorized operation
        return select(
            [
                person("is_military", period),
                person("has_never_worked", period),
                person("is_executive_administrative_professional", period),
                person("is_farmer_fisher", period),
                person("is_computer_scientist", period),
                True,  # Default case
            ],
            [
                OvertimeExemptionCategory.MILITARY,
                OvertimeExemptionCategory.NEVER_WORKED,
                OvertimeExemptionCategory.EXECUTIVE_ADMINISTRATIVE,
                OvertimeExemptionCategory.FARMER_FISHER,
                OvertimeExemptionCategory.COMPUTER_SCIENTIST,
                OvertimeExemptionCategory.NONE,
            ],
        )
