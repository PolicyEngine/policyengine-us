from policyengine_us.model_api import *


class utilities_included_in_rent(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether heat, utilities, furniture, or similar items are included in rent payments"
    definition_period = YEAR
    documentation = "Whether the rent covers heat, utilities, furniture, or similar items (Maine Schedule PTFC line 5b). The Michigan home heating credit reads the narrower heat_expense_included_in_rent and treats this flag as implying heat is included. Overlaps the household-level tenant_pays_utilities input; reconciliation is tracked separately."
