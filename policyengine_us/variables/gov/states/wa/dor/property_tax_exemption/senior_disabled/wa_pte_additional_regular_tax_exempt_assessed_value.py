from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wa.dor.property_tax_exemption.senior_disabled.wa_senior_disabled_property_tax_exemption import (
    regular_exempt_assessed_value,
)


class wa_pte_additional_regular_tax_exempt_assessed_value(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    quantity_type = STOCK
    label = (
        "Washington assessed value exempt from remaining regular property tax levies"
    )
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://lawfilesext.leg.wa.gov/biennium/2023-24/Htm/Bills/Session%20Laws/House/1355-S.SL.htm",  # RCW 84.36.381(5)(b) as applicable to 2025 collection
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-140",  # (2)(b)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.dor.property_tax_exemption.senior_disabled
        if not p.reported_regular_exemption_in_effect:
            return 0

        assessed_value = tax_unit("wa_pte_assessor_approved_value", period)
        tier = tax_unit("wa_pte_reported_tier", period)
        return regular_exempt_assessed_value(assessed_value, tier, p.benefit)
