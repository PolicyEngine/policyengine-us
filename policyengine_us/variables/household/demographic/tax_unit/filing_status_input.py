from policyengine_us.model_api import *


class FilingStatusInput(Enum):
    UNSPECIFIED = "Unspecified"
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    SURVIVING_SPOUSE = "Surviving spouse"


class filing_status_input(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatusInput
    default_value = FilingStatusInput.UNSPECIFIED
    definition_period = YEAR
    label = "Supplied filing status"
    documentation = "The tax unit's filing status as assigned by the tax-unit constructor that built a dataset, such as the Populace US build. When supplied, filing_status uses it; a supplied JOINT status requires a spouse in the unit, and a unit with a spouse must be supplied JOINT. UNSPECIFIED (the default) means the status was not supplied, and filing_status is derived from the unit's members and the head of household and surviving spouse rules. A supplied status is a fact about the record, so parameter reforms to those rules, such as the dependent age limits, do not re-derive it; a structural reform that removes a status must neutralize this variable, as remove_head_of_household does."
