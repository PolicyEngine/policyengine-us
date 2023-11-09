from policyengine_us.model_api import *


class KyFilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"


class ky_filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = KyFilingStatus
    default_value = KyFilingStatus.SINGLE
    definition_period = YEAR
    label = "Filing status for the tax unit in Kentucky"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        has_spouse = add(tax_unit, period, ["is_tax_unit_spouse"]) > 0
        person = tax_unit.members
        is_separated = tax_unit.any(person("is_separated", period))
        return select(
            [
                has_spouse,
                is_separated,
                True,
            ],
            [
                KyFilingStatus.JOINT,
                KyFilingStatus.SEPARATE,
                KyFilingStatus.SINGLE,
            ],
        )
