from policyengine_us.model_api import *


class pr_actc_modified_income_excess_applies(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Puerto Rico condition if modified AGI greater than threshold"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"

    def formula(tax_unit, period, parameters):
        # line 5
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.actc.income_limit
        modified_agi = tax_unit("pr_modified_agi", period)
        filing_status = tax_unit("filing_status", period)

        threshold = select(
            [
                filing_status == filing_status.possible_values.JOINT,
                filing_status != filing_status.possible_values.JOINT,
            ],
            [
                p.joint,
                p.other,
            ],
        )

        return modified_agi > threshold
