from policyengine_us.model_api import *


class utilities_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether heat, utilities, furniture, or similar items are included in rent payments"
    documentation = "Derived as the inverse of the household-level tenant_pays_utilities input, projected to the tax unit; it can still be set directly. Read by the Maine property tax fairness credit (Schedule PTFC line 5b) and, as implying heat is included, by the Michigan home heating credit."
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_pstfc_ff.pdf#page=2"

    def formula(tax_unit, period, parameters):
        return ~tax_unit.household("tenant_pays_utilities", period)
