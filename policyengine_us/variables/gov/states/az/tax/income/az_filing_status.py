from policyengine_us.model_api import *


class ArizonaFilingStatus(Enum):
    SINGLE = "Single"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    JOINT = "Joint"


class az_filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = ArizonaFilingStatus
    default_value = ArizonaFilingStatus.SINGLE
    definition_period = YEAR
    documentation = "https://azdor.gov/forms/individual/form-140a-arizona-resident-personal-income-tax-booklet"  # Page 5, Box 5
    label = "Arizona filing status"

    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        us_filing_status = tax_unit("filing_status", period)
        fsvals = us_filing_status.possible_values
        return select(
            [
                us_filing_status == fsvals.JOINT,
                us_filing_status == fsvals.SINGLE,
                us_filing_status == fsvals.SEPARATE,
            ],
            [
                # In Arizona, widowed filers are treated as heads of households.
                ArizonaFilingStatus.JOINT,
                ArizonaFilingStatus.SINGLE,
                ArizonaFilingStatus.SEPARATE,
            ],
            default=ArizonaFilingStatus.HEAD_OF_HOUSEHOLD,
        )
