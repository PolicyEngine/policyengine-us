from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)


def create_remove_head_of_household() -> Reform:
    class filing_status(Variable):
        value_type = Enum
        entity = TaxUnit
        possible_values = FilingStatus
        default_value = FilingStatus.SINGLE
        definition_period = YEAR
        label = "Filing status"

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
                has_spouse,
                is_separated,
                widowed_head_with_dependents,
            ],
            [
                FilingStatus.JOINT,
                FilingStatus.SEPARATE,
                FilingStatus.WIDOW,
            ],
            default=FilingStatus.SINGLE,
        )

    class reform(Reform):
        def apply(self):
            self.update_variable(filing_status)

    return reform


def create_remove_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_head_of_household()

    p = parameters(period).gov.contrib.congress.romney.family_security_act

    if p.remove_head_of_household is True:
        return create_remove_head_of_household()
    else:
        return None


remove_head_of_household = create_remove_head_of_household_reform(
    None, None, bypass=True
)
