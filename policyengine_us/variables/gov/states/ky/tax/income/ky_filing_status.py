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
    reference = (
        "https://codes.findlaw.com/ky/title-xi-revenue-and-taxation/ky-rev-st-sect-141-066.html",  # Section (1), (c) & (d)
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11",
    )
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
            ],
            [
                KyFilingStatus.JOINT,
                KyFilingStatus.SEPARATE,
            ],
            default=KyFilingStatus.SINGLE,
        )
