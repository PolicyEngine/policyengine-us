from policyengine_us.model_api import *


class refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable American Opportunity Credit"
    unit = USD
    documentation = "Value of the refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title26-section25A"

    def formula(tax_unit, period, parameters):
        aoc = parameters(period).gov.irs.credits.education.american_opportunity_credit
        return aoc.refundability * tax_unit("american_opportunity_credit", period)
