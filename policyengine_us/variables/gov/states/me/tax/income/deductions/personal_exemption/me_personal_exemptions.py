from policyengine_us.model_api import *


class me_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_dwnld_ff.pdf"

    def formula(tax_unit, period, parameters):
        # Get filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine ME personal exemption which varies only with filing status according to Instructions for Line 13
        filing_statuses = filing_status.possible_values
        personal_exemption = select(
            [
                filing_status == filing_statuses.SINGLE,
                filing_status == filing_statuses.JOINT,
                filing_status == filing_statuses.SEPARATE,
                filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                filing_status == filing_statuses.WIDOW,
            ],
            [
                1,
                2,
                1,
                1,
                1,
            ],
        )

        return personal_exemption
