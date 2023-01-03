from policyengine_us.model_api import *


class in_oos_municipal_obligation_interest_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN out-of-state municipal obligation interest add back"
    definition_period = YEAR
    documentation = "Add back for interest earned from a direct obligation of a state or political subdivision other than Indiana for obligations purchased after Dec. 31, 2011."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(21)
    # use (total state/municipal obligation interest) - (Indiana's) if those data are added later
