from policyengine_us.model_api import *


class mn_mfip_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06#stat.256P.06.3"
    )
    defined_for = StateCode.MN
    # Per MN Stat. 256P.06, Subd. 3:
    # Gross unearned income minus child support exclusion (up to $100/1 child, $200/2+).
    adds = ["tanf_gross_unearned_income"]
    subtracts = ["mn_mfip_child_support_income_exclusion"]
