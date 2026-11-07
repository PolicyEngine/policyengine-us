from policyengine_us.model_api import *


class veterans_benefits(Variable):
    value_type = float
    entity = Person
    label = "Veterans benefits"
    unit = USD
    documentation = (
        "Benefits the Department of Veterans Affairs pays from past military "
        "service, such as disability compensation, pensions, dependency and "
        "indemnity compensation to survivors, and education allowances. "
        "38 U.S.C. 5301(a)(1) exempts them from taxation, so federal gross "
        "income leaves them out. Census money income counts them as veterans' "
        "payments, and household and SPM benefits include them. Military "
        "retirement pay goes in military_retirement_pay instead."
    )
    definition_period = YEAR
    uprating = "gov.ssa.uprating"
    reference = (
        "https://www.law.cornell.edu/uscode/text/38/5301#a_1",
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=3",
    )
