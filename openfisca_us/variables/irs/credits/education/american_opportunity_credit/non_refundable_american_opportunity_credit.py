from openfisca_us.model_api import *


class non_refundable_american_opportunity_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Non-refundable American Opportunity Credit"
    unit = USD
    documentation = "Value of the non-refundable portion of the American Opportunity Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#i"

    def formula(tax_unit, period):
        total = tax_unit("american_opportunity_credit", period)
        refundable = tax_unit("refundable_american_opportunity_credit", period)
        return total - refundable
