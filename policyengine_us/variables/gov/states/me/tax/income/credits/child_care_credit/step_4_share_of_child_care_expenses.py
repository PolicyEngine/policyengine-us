from policyengine_us.model_api import *


class step_4_share_of_child_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine step 4 share of child care expenses"
    documentation = "Share of child care expenses that are from programs classified as Step 4 in Maine"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html"
    defined_for = StateCode.ME
