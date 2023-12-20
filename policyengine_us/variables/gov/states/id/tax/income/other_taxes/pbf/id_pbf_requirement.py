from policyengine_us.model_api import *


class id_pbf_requirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Required to pay the Idaho permanent building fund tax"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Not required to pay the PBF if there is no income tax
        income_tax_payment = (
            tax_unit("id_income_tax_before_non_refundable_credits", period) > 0
        )

        # Not required to pay the PBF if receiving public assistance, tanf
        tanf_received = tax_unit.spm_unit("tanf", period) > 0

        # Not required to pay the PBF if head or spouse is blind
        blind_head = tax_unit("blind_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        blind_head_or_spouse = blind_head | blind_spouse

        return income_tax_payment & ~tanf_received & ~blind_head_or_spouse
