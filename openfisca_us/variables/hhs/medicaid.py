from openfisca_us.model_api import *
from openfisca_us.variables.demographic.spm_unit import spm_unit_assets


class MedicaidPersonType(Enum):
    ADULT_WITHOUT_DEPENDENT = "Adult without dependent"
    ADULT_WITH_DEPENDENT = "Adult with dependent"
    CHILD_AGE_0 = "Child age 0"
    CHILD_AGE_1_5 = "Child age 1 to 5"
    CHILD_AGE_6_18 = "Child age 6 to 18"


class medicaid_person_type(Variable):
    value_type = Enum
    possible_values = MedicaidPersonType
    default_value = MedicaidPersonType.ADULT_WITHOUT_DEPENDENT
    entity = Person
    definition_period = YEAR
    label = "Medicaid person type"
    documentation = "Person type for Medicaid"

    def formula(person, period, parameters):
        over_65 = person("age", period) >= 65
        pregnant = person("is_pregnant", period)
        disabled = person("is_disabled", period)
        return disabled | over_65 | pregnant


class medicaid_income_threshold(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Medicaid FPL threshold"
    documentation = "Maximum income as a percentage of the federal poverty line to qualify for Medicaid"

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        person_type = person("medicaid_person_type", period)
        income_threshold = parameters(period).hhs.medicaid.income_limit
        return income_threshold[state_code][person_type]


class is_medicaid_eligible(Variable):
    value_type: bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligibility for Medicaid"
    documentation = (
        "Whether the person is eligible for Medicaid health benefit."
    )

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit.any(
            spm_unit_assets.members("medicaid_person_type", period)
        )
        economic_eligible = where(spm_unit(medicaid_income_threshold, period),)
        return demographic_eligible | economic_eligible

