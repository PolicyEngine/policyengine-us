from policyengine_us.model_api import *


class az_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona adjusted gross income"
    unit = USD
    definition_period = YEAR
    documentation = "https://azdor.gov/sites/default/files/2023-03/FORMS_INDIVIDUAL_2020_140NRBOOKLET.pdf#page=18"  # Line 52
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        additions = tax_unit("az_additions", period)
        subtractions = tax_unit("az_subtractions", period)
        exemptions = tax_unit("az_exemptions", period)

        return max_(
            0, adjusted_gross_income + additions - subtractions - exemptions
        )
