from policyengine_us.model_api import *


class CHIPCategory(Enum):
    CHILD = "Child"
    PREGNANT_STANDARD = "Pregnant - Standard"
    PREGNANT_FCEP = "Pregnant - FCEP"
    NONE = "None"


class chip_category(Variable):
    value_type = Enum
    possible_values = CHIPCategory
    default_value = CHIPCategory.NONE
    entity = Person
    label = "CHIP category"
    documentation = "Category under which a person is eligible for the Children's Health Insurance Program"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/ssact/title21/2110.htm",
        "https://www.medicaid.gov/medicaid/national-medicaid-chip-program-information/medicaid-childrens-health-insurance-program-basic-health-program-eligibility-levels",
        "https://www.kff.org/affordable-care-act/state-indicator/medicaid-and-chip-income-eligibility-limits-for-pregnant-women-as-a-percent-of-the-federal-poverty-level",
    )

    def formula(person, period, parameters):
        is_child_eligible = person("is_chip_eligible_child", period)
        is_chip_eligible_standard_pregnant_person = person(
            "is_chip_eligible_standard_pregnant_person", period
        )
        is_chip_fcep_eligible_person = person(
            "is_chip_fcep_eligible_person", period
        )

        # Use select to return the appropriate category
        # If eligible under multiple categories, prioritize child, then standard pregnant, then FCEP
        return select(
            [
                is_child_eligible,
                is_chip_eligible_standard_pregnant_person,
                is_chip_fcep_eligible_person,
            ],
            [
                CHIPCategory.CHILD,
                CHIPCategory.PREGNANT_STANDARD,
                CHIPCategory.PREGNANT_FCEP,
            ],
            default=CHIPCategory.NONE,
        )
