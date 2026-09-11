from policyengine_us.model_api import *


class MassachusettsFilingStatus(Enum):
    SINGLE = "Single"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    JOINT = "Joint"


class ma_filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = MassachusettsFilingStatus
    default_value = MassachusettsFilingStatus.SINGLE
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/filing-status-on-massachusetts-personal-income-tax"
    label = "Massachusetts filing status"
    defined_for = StateCode.MA

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
                MassachusettsFilingStatus.JOINT,
                MassachusettsFilingStatus.SINGLE,
                MassachusettsFilingStatus.SEPARATE,
            ],
            # Massachusetts has no surviving spouse filing status; federal
            # qualifying surviving spouses generally file as head of household.
            default=MassachusettsFilingStatus.HEAD_OF_HOUSEHOLD,
        )
