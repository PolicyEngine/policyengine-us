from policyengine_us.model_api import *


class pr_american_opportunity_credit_eligibility(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico American Opportunity Credit Eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=14"
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.american_opportunity_credit.agi_limit

        filing_status = tax_unit("filing_status", period)
        not_separate = filing_status != filing_status.possible_values.SEPARATE

        agi = tax_unit("pr_agi", period)
        filing_status = tax_unit("filing_status", period)
        agi_limit = where(
            filing_status == filing_status.possible_values.SINGLE,
            p.single,
            p.joint,
        )
        agi_eligibility = agi < agi_limit
        return not_separate & agi_eligibility
