from policyengine_us.model_api import *


class mn_paid_leave_employer_average_quarterly_wage(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Paid Leave employer average quarterly wage"
    documentation = (
        "Average wage of the person's employer as Minnesota Paid Leave "
        "measures it for the small employer premium rate: the employer's "
        "covered wages in its highest-paid quarter of the basis period (the "
        "four quarters ending September 30 of the prior year) divided by its "
        "highest quarterly employee count in that period; the two may come "
        "from different quarters (Minn. Stat. 268B.14, subds. 5b(a) and "
        "5c(a)). An employer not covered for the whole basis period uses its "
        "own estimates instead (subd. 5c(b)). The default of 0 treats the "
        "employer as meeting the wage test, so employer_headcount alone "
        "decides whether the small employer rate applies."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.revisor.mn.gov/statutes/cite/268B.14"
