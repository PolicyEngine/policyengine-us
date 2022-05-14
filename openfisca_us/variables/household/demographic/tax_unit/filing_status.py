from openfisca_us.model_api import *


class FilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    WIDOW = "Widow(er)"


class filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    definition_period = YEAR
    label = "Filing status for the tax unit"

    def formula(tax_unit, period, parameters):
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        has_dependents = tax_unit("tax_unit_dependents", period) > 0
        return select(
            [has_spouse, has_dependents, True],
            [
                FilingStatus.JOINT,
                FilingStatus.HEAD_OF_HOUSEHOLD,
                FilingStatus.SINGLE,
            ],
        )


# For Tax-Calculator.
mars = variable_alias("mars", filing_status)
