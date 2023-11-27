from policyengine_us.model_api import *


def create_remove_standard_deduction_head_of_household() -> Reform:
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
        label = "Filing_status (Eliminating HoH)"
        documentation = "Eliminating HoH under the tax foundation growth and opportunity plan"

        def formula(tax_unit, period, parameters):
            has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
            person = tax_unit.members
            is_separated = tax_unit.any(person("is_separated", period))
            is_widowed = tax_unit.any(person("is_widowed", period))
            return select(
                [
                    has_dependents & ~has_spouse,
                    has_spouse,
                    is_separated,
                    is_widowed,
                    True,
                ],
                [
                    FilingStatus.SINGLE,
                    FilingStatus.JOINT,
                    FilingStatus.SEPARATE,
                    FilingStatus.WIDOW,
                    FilingStatus.SINGLE,
                ],
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(filing_status)

    return reform


def create_remove_standard_deduction_head_of_household_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_remove_standard_deduction_head_of_household()

    p = parameters(period).gov.contrib.tax_foundation.growth_and_opportunity

    if p.remove_head_of_household is True:
        return create_remove_standard_deduction_head_of_household()
    else:
        return None


remove_standard_deduction_head_of_household = (
    create_remove_standard_deduction_head_of_household_reform(
        None, None, bypass=True
    )
)
