from policyengine_us.model_api import *
from numpy import ceil


class pr_actc_modified_income_calculation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico income modification for additional child tax credit computation"
    definition_period = YEAR
    reference = "https://www.irs.gov/pub/irs-pdf/f1040ss.pdf#page=2"
    defined_for = "pr_agi_greater_than_threshold"

    # only compute if modified_agi > threshold
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits
        modified_agi = tax_unit("pr_modified_agi", period)
        filing_status = tax_unit("filing_status", period)

        threshold = select(
            [
                filing_status == filing_status.possible_values.JOINT,
                filing_status != filing_status.possible_values.JOINT,
            ],
            [
                p.ctc.income_limit_joint,
                p.ctc.income_limit_all_other,
            ],
        )

        # calculate credit based on income earned over the threshold, lines 5 & 6
        modified_inc = modified_agi - threshold 
        multiple = p.actc.income_multiple
        # turn it into a multiple of 1000 if not already
        modified_inc = int(ceil(modified_inc / multiple)[0] * multiple) * p.actc.income_rate
        
        return modified_inc