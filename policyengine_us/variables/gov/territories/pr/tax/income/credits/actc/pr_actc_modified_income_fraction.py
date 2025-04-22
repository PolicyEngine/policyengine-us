from policyengine_us.model_api import *
from numpy import ceil


class pr_actc_modified_income_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico ACTC modified income threshold"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2" # line 6
    documentation = "The Puerto Rico ACTC is limited to the smaller of the actual credit amount and this value derived from the modified AGI."
    defined_for = "pr_actc_modified_income_excess_applies"

    # only compute if modified_agi > threshold
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.actc
        modified_agi = tax_unit("pr_modified_agi", period)
        filing_status = tax_unit("filing_status", period)

        threshold = select(
            [
                filing_status == filing_status.possible_values.JOINT,
                filing_status != filing_status.possible_values.JOINT,
            ],
            [
                p.income_limit.joint,
                p.income_limit.other,
            ],
        )

        # calculate credit based on income earned over the threshold, lines 5 & 6
        modified_inc = modified_agi - threshold
        # turn it into a multiple of 1000 if not already
        income_fraction = (
            int(ceil(modified_inc / p.income_multiple) * p.income_multiple)
        )

        return income_fraction * p.income_rate
