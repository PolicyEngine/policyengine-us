from policyengine_us.model_api import *


class utilities_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether heat, utilities, furniture, or similar items are included in rent payments"
    definition_period = YEAR
    documentation = "Whether the rent covers heat, utilities, furniture, or similar items (Maine Schedule PTFC line 5b). This does not establish that heat is included. For the Michigan home heating credit, use heat_expense_included_in_rent or mi_home_heating_credit_heat_included_in_rent. Overlaps the household-level tenant_pays_utilities input; reconciliation is tracked separately."
