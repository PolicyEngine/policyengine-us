from policyengine_us.model_api import *


class me_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_2_ff.pdf"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5125.html"
    defined_for = StateCode.ME
