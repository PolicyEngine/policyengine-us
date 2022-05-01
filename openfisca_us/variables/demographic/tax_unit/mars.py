from openfisca_us.model_api import *


class MARSType(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    WIDOW = "Widow(er)"


class mars(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = MARSType
    default_value = MARSType.SINGLE
    definition_period = YEAR
    label = "Marital status for the tax unit"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        has_dependents = tax_unit("tax_unit_dependents", period) > 0
        return select(
            [has_spouse, has_dependents, True],
            [MARSType.JOINT, MARSType.HEAD_OF_HOUSEHOLD, MARSType.SINGLE],
        )


marital_status = variable_alias("marital_status", mars)
