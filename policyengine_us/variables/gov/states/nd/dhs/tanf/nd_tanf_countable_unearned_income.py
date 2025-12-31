from policyengine_us.model_api import *


class nd_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://nd.gov/dhs/policymanuals/40019/Archive%20Documents/2021%20-%20ML3629/Copy%20of%20400_19_55_25.htm"
    defined_for = StateCode.ND

    # Per 400-19-55-25: Unearned income is counted without deductions
    # (various exclusions like SSI, SNAP, LIHEAP are already excluded
    # in the federal tanf_gross_unearned_income definition)
    adds = ["tanf_gross_unearned_income"]
