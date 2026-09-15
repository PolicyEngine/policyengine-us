from policyengine_us.model_api import *


class utilities_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether heat, utilities, furniture, or similar items are included in rent payments"
    documentation = (
        "Whether the rent covers heat, utilities, furniture, or similar items "
        "(Maine Schedule PTFC line 5b). Derived as the inverse of the "
        "household-level tenant_pays_utilities input, projected to the tax "
        "unit; it can still be set directly. Read by the Maine property tax "
        "fairness credit. This does not establish that heat is included: the "
        "Michigan home heating credit reads heat_expense_included_in_rent "
        "instead."
    )
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/25_1040me_sch_ptfc_fillable.pdf#page=1"

    def formula(tax_unit, period, parameters):
        # The household value broadcasts to every tax unit in the household;
        # a direct input on this variable is the only way to differentiate
        # tax units that share a household.
        return ~tax_unit.household("tenant_pays_utilities", period)
