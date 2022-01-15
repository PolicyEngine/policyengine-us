from openfisca_us.model_api import *


class SNAPUttilityAllowanceType(Enum):
    SUA = "Standard Utility Allowance"
    LUA = "Limited Utility Allowance"
    TUA = "Telephone Utility Allowance"
    NONE = "None"


class snap_utility_allowance_type(Variable):
    value_type = Enum
    possible_values = SNAPUttilityAllowanceType
    entity = SPMUnit
    label = "SNAP utility allowance eligibility"
    default_value = SNAPUttilityAllowanceType.NONE
    documentation = (
        "The type of utility allowance that is eligible for the SPM unit"
    )
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        household = spm_unit.household
        return select(
            [
                household("has_heating_cooling_expense", period),
                household("has_other_utility_expense", period),
                household("has_telephone_expense", period),
                True,
            ],
            [
                SNAPUttilityAllowanceType.SUA,
                SNAPUttilityAllowanceType.LUA,
                SNAPUttilityAllowanceType.TUA,
                SNAPUttilityAllowanceType.NONE,
            ],
        )
