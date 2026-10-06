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
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=49188",  # KRS 141.066(1)(c) & (d)
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11",
        "https://revenue.ky.gov/Forms/740%20instructions%20packet%20(2024).pdf#page=13",
    )
    label = "Filing status for the tax unit in Kentucky"
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        # Kentucky follows the filer's own federal marital status (IRC 7703),
        # so a separated dependent does not make the filer file separately.
        # Federal head of household and surviving spouse filers use
        # Kentucky Filing Status 1 (Single).
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        return select(
            [
                filing_status == statuses.JOINT,
                filing_status == statuses.SEPARATE,
            ],
            [
                KyFilingStatus.JOINT,
                KyFilingStatus.SEPARATE,
            ],
            default=KyFilingStatus.SINGLE,
        )
