from policyengine_us.model_api import *


class az_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Property Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(B), (G)
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=5",
    ]
    defined_for = "az_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        # ARS 43-1072(G): one claimant per household per year. Every other
        # eligible tax unit in the household gets no credit.
        potential = tax_unit("az_property_tax_credit_potential", period)
        claimant = tax_unit("az_property_tax_credit_claimant", period)
        return potential * claimant
