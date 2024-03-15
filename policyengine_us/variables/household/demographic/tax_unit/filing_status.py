from policyengine_us.model_api import *


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
        person = tax_unit.members
        has_spouse = tax_unit.any(person("is_tax_unit_spouse", period))
        has_dependents = tax_unit.any(person("is_child_dependent", period))
        is_separated = tax_unit.any(person("is_separated", period))
        # The widowed filing status should only apply to widowed heads
        # who maintain a household for at least one dependent
        is_head = person("is_tax_unit_head", period)
        is_widowed = person("is_widowed", period)
        widowed_head = tax_unit.any(is_head & is_widowed)
        widowed_head_with_dependents = widowed_head & has_dependents
        return select(
            [
                has_dependents & ~has_spouse & ~widowed_head,
                has_spouse,
                is_separated,
                widowed_head_with_dependents,
            ],
            [
                FilingStatus.HEAD_OF_HOUSEHOLD,
                FilingStatus.JOINT,
                FilingStatus.SEPARATE,
                FilingStatus.WIDOW,
            ],
            default=FilingStatus.SINGLE,
        )
