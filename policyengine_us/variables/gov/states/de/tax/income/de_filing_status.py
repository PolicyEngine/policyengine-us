from policyengine_us.model_api import *


class FilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    WIDOW = "Widow(er)"
    COMBINED_SEPARATE = "Combined Separate"


class filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    definition_period = YEAR
    label = "Delaware Filing status for the tax unit"

    def formula(tax_unit, period, parameters):
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        has_dependents = tax_unit("tax_unit_dependents", period) > 0
        person = tax_unit.members
        is_separated = tax_unit.any(person("is_separated", period))
        is_widowed = tax_unit.any(person("is_widowed", period))
        is_return_combined = tax_unit.any(person("is_return_combined", period))
        return select(
            [
                has_dependents & ~has_spouse,
                has_spouse,
                is_separated,
                is_widowed,
                is_separated & is_return_combined
                True,
            ],
            [
                FilingStatus.HEAD_OF_HOUSEHOLD,
                FilingStatus.JOINT,
                FilingStatus.SEPARATE,
                FilingStatus.WIDOW,
                FilingStatus.COMBINED_SEPARATE
                FilingStatus.SINGLE,
            ],
        )