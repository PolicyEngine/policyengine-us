from policyengine_us.model_api import *


class ssdi_work_credits(Variable):
    value_type = int
    entity = Person
    label = "SSDI work credits"
    definition_period = YEAR
    reference = "https://www.ssa.gov/benefits/retirement/planner/credits.html"
    documentation = """
    Number of work credits earned for SSDI eligibility.
    Generally, you earn 1 credit for each $1,730 in earnings (2024), up to 4 credits per year.

    Per 42 USC 413, credits are calculated from covered earnings history.
    Since PolicyEngine lacks historical earnings data, this is an input variable.
    Users should provide total credits earned based on their work history.
    """
