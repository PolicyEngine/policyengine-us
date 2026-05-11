from policyengine_us.model_api import *


class wa_pte_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Washington Senior Citizens and Disabled Persons Property Tax Exemption"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        has_categorical_member = (
            add(tax_unit, period, ["wa_pte_categorical_eligible"]) > 0
        )
        # Owner-occupancy proxy: only homeowners pay real_estate_taxes directly.
        pays_property_tax = add(tax_unit, period, ["real_estate_taxes"]) > 0
        income_eligible = tax_unit("wa_pte_income_eligible", period)
        return has_categorical_member & pays_property_tax & income_eligible
