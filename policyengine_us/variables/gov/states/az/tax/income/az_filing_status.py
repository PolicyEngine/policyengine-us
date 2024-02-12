from policyengine_us.model_api import *


class StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn(Enum):
    SINGLE = "Single"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    WIDOW = "Widow(er)"
    JOINT = "Joint"


class az_filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn
    default_value = (
        StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.SINGLE
    )
    definition_period = YEAR
    label = "Arizona filing status"

    def formula(tax_unit, period, parameters):
        us_filing_status = tax_unit("filing_status", period)
        fsvals = us_filing_status.possible_values
        return select(
            [
                us_filing_status == fsvals.JOINT,
                us_filing_status == fsvals.SINGLE,
                us_filing_status == fsvals.SEPARATE,
                us_filing_status == fsvals.HEAD_OF_HOUSEHOLD,
                us_filing_status == fsvals.WIDOW,
            ],
            [
                # Simulate scenario where joint filers file separately on Arkansas return.
                StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.JOINT,
                StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.SINGLE,
                StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.SEPARATE,
                StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.HEAD_OF_HOUSEHOLD,
                StateFilingStatusIfMarriedFilingSeparatelyOnSameReturn.HEAD_OF_HOUSEHOLD,
            ],
        )
