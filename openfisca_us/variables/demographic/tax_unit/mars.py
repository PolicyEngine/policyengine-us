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
        spouse_with_age = person("is_tax_unit_spouse", period)
        has_age = person("age", period) > 0
        has_spouse_with_age = tax_unit.any(spouse_with_age & has_age)
        return where(has_spouse_with_age, MARSType.JOINT, MARSType.SINGLE)


marital_status = variable_alias("marital_status", mars)
