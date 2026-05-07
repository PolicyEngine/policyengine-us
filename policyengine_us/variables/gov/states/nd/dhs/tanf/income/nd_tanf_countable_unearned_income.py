from policyengine_us.model_api import *


class nd_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Dakota TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.nd.gov/dhs/policymanuals/40019/400_19_55_25.htm"
    defined_for = StateCode.ND

    # Child support received assigned to Child Support Division is excluded.
    # Result cannot be negative since child_support_received is a component
    # of tanf_gross_unearned_income.
    adds = ["tanf_gross_unearned_income"]
    subtracts = ["child_support_received"]
