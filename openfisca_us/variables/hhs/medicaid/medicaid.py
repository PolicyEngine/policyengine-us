from openfisca_us.model_api import *


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
        # Get the person's age.
        age = person("age", period)
        # Get the existence of dependents, as defined by people 18 or younger.
        has_dependents = person.spm_unit.any(
            person.spm_unit.members("age", period) < 19
        )
        return select(
            [age == 0, age < 6, age < 19, has_dependents, True],
            [
                MedicaidPersonType.CHILD_AGE_0,
                MedicaidPersonType.CHILD_AGE_1_5,
                MedicaidPersonType.CHILD_AGE_6_18,
                MedicaidPersonType.ADULT_WITH_DEPENDENT,
                MedicaidPersonType.ADULT_WITHOUT_DEPENDENT,
            ],
        )


class medicaid_income_threshold(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Medicaid FPL threshold"
    documentation = "Maximum income as a percentage of the federal poverty line to qualify for Medicaid"
    unit = "percent"

    def formula(person, period, parameters):
        state_code = person.household("state_code_str", period)
        person_type = person("medicaid_person_type", period)
        income_threshold = parameters(period).hhs.medicaid.income_limit
        return income_threshold[state_code][person_type]


class medicaid_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Medicaid gross income"
    documentation = "Gross income for calculating Medicaid eligibility"
    unit = "currency-USD"

    def formula(spm_unit, period):
        return spm_unit.sum(spm_unit.members("market_income", period))


class meets_medicaid_income_threshold(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets Medicaid income threshold"
    documentation = "Whether the person meets the Medicaid income threshold given their state, age, and family structure."

    def formula(person, period, parameters):
        income = person.spm_unit("medicaid_gross_income", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        fpg_income_threshold = person("medicaid_income_threshold", period)
        income_share_of_fpg = income / fpg
        return income_share_of_fpg <= fpg_income_threshold


class medicaid(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Estimated benefit amount from Medicaid"
    label = "Medicaid benefit"
    unit = "currency-USD"
