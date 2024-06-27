from policyengine_us.model_api import *


class PellGrantHouseholdType(Enum):
    DEPENDENT_SINGLE = "Dependent single"
    DEPENDENT_NOT_SINGLE = "Dependent not single"
    INDEPENDENT_SINGLE = "Independent single"
    INDEPENDENT_NOT_SINGLE = "Independent not single"


class pell_grant_household_type(Variable):
    value_type = Enum
    possible_values = PellGrantHouseholdType
    default_value = PellGrantHouseholdType.INDEPENDENT_SINGLE
    entity = Person
    definition_period = YEAR
    label = "Pell Grant household type"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        joint = person.tax_unit("tax_unit_is_joint", period)

        return select(
            [
                dependent & ~joint,
                dependent & joint,
                ~dependent & ~joint,
                ~dependent & joint,
            ],
            [
                PellGrantHouseholdType.DEPENDENT_SINGLE,
                PellGrantHouseholdType.DEPENDENT_NOT_SINGLE,
                PellGrantHouseholdType.INDEPENDENT_SINGLE,
                PellGrantHouseholdType.INDEPENDENT_NOT_SINGLE,
            ],
        )
