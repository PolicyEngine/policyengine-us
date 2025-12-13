from policyengine_us.model_api import *


class az_property_tax_credit_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income for property tax credit"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Adjusted gross income as defined for Arizona property tax credit purposes. "
        "Per ARS 43-1072(H)(6) and Arizona Admin Code R15-2C-502, this is Federal AGI "
        "plus Arizona additions minus Arizona subtractions, but does NOT include "
        "the deduction for Arizona exemptions (aged, blind, etc.)."
    )
    reference = [
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(H)(6)
        "https://apps.azsos.gov/public_services/Title_15/15-02.pdf",  # Arizona Admin Code R15-2C-502
    ]
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # Start with Federal AGI
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)

        # Add Arizona-specific additions
        additions = tax_unit("az_additions", period)

        # Subtract Arizona-specific subtractions
        subtractions = tax_unit("az_subtractions", period)

        # NOTE: Unlike az_agi, we do NOT subtract az_exemptions here
        # Per ARS 43-1072(H)(6) and Admin Code R15-2C-502, the property tax credit
        # uses a definition that does not include Arizona exemptions

        return max_(
            0, adjusted_gross_income + additions - subtractions
        )
