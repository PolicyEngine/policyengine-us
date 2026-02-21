from policyengine_us.model_api import *


class ssdi_recent_work_credits(Variable):
    value_type = int
    entity = Person
    label = "SSDI recent work credits"
    definition_period = YEAR
    reference = "https://www.ssa.gov/benefits/disability/qualify.html"
    documentation = """
    Number of work credits earned in the recent work period for SSDI.
    Generally, 20 credits must be earned in the last 10 years for those over 31.

    Per 42 USC 423(c)(1)(B), recent work requirements vary by age.
    Since PolicyEngine lacks historical earnings data, this is an input variable.
    Users should provide credits earned in the recent work period.
    """
