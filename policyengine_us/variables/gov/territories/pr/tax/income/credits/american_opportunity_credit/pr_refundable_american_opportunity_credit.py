from policyengine_us.model_api import *


class pr_refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico Refundable American Opportunity Credit"
    unit = USD
    documentation = "Puerto Rico value of the refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=13"
    defined_for = "pr_american_opportunity_credit_eligibility"

    def formula(tax_unit, period, parameters):
        aoc = parameters(
            period
        ).gov.irs.credits.education.american_opportunity_credit
        return aoc.refundability * tax_unit(
            "pr_american_opportunity_credit", period
        )
