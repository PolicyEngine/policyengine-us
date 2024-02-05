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
            has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
            person = tax_unit.members
            is_separated = tax_unit.any(person("is_separated", period))
            is_widowed = tax_unit.any(person("is_widowed", period))
            return select(
                [has_spouse, is_separated, is_widowed],
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
