from policyengine_us.model_api import *


class id_pbf_requirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Required to pay the Idaho permanent building fund tax"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # eligible if income less than filing status specified amount
        income_ineligible = (
            tax_unit("id_income_tax_before_non_refundable_credits", period)
            <= 0
        )

        # eligible if receiving public assistance tanf
        tanf_received = tax_unit.spm_unit("tanf", period) > 0

        # eligible if head or spouse is blind
        blind_head = tax_unit("blind_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        blind_ineligible = blind_head | blind_spouse

        return ~income_ineligible & ~tanf_received & ~blind_ineligible
