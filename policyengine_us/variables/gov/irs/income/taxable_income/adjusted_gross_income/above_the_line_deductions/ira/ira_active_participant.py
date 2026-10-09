from policyengine_us.model_api import *


class ira_active_participant(Variable):
    value_type = bool
    entity = Person
    label = "Active participant in an employer retirement plan for IRA deductions"
    definition_period = YEAR
    default_value = False
    documentation = (
        "Whether this person was an active participant for any part of a plan "
        "year ending within the tax year in a plan covered by section 219(g)(5), "
        "including defined benefit, 401(a), 403(a), 403(b), SEP and SIMPLE plans. "
        "Use the person's own coverage, generally reported in Form W-2 box 13; "
        "do not include a spouse's coverage or participation solely in a 457(b) "
        "plan. Apply the reserve and volunteer firefighter exceptions in "
        "section 219(g)(6)."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_5",
        "https://www.irs.gov/instructions/iw2w3",
    )
