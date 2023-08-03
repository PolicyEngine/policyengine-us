from policyengine_us.model_api import *


class me_step_4_share_of_child_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine Step 4 Share of Child Care Expenses"
    documentation = "Share of child care expenses that are from programs classified as Step 4 in Maine"
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_a_ff.pdf"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5218.html"
