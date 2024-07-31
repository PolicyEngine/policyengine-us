from policyengine_us.model_api import *


class FilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    SURVIVING_SPOUSE = "Surviving spouse"


class filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    definition_period = YEAR
    label = "Filing status for the tax unit"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_separated = tax_unit.any(person("is_separated", period))
        return select(
            [
                is_separated,
                tax_unit("tax_unit_married", period),
                tax_unit("surviving_spouse_eligible", period),
                tax_unit("head_of_household_eligible", period),
            ],
            [
                FilingStatus.SEPARATE,
                FilingStatus.JOINT,
                FilingStatus.SURVIVING_SPOUSE,
                FilingStatus.HEAD_OF_HOUSEHOLD,
            ],
            default=FilingStatus.SINGLE,
        )
