from policyengine_us.model_api import *


class veterans_benefits(Variable):
    value_type = float
    entity = Person
    label = "Veterans benefits"
    unit = USD
    documentation = (
        "Tax-exempt payments for past military service: benefits the "
        "Department of Veterans Affairs pays, such as disability compensation, "
        "pensions, dependency and indemnity compensation to survivors, and "
        "education allowances, and Combat-Related Special Compensation (CRSC), "
        "which the military departments pay under 10 U.S.C. 1413a. "
        "38 U.S.C. 5301(a)(1) exempts VA benefits from taxation, and IRS "
        "Publication 525 lets retirees exclude CRSC from income, so federal "
        "gross income leaves both out. Census money income counts VA payments "
        "as veterans' payments, and household and SPM benefits include this "
        "variable. Taxable military retirement pay goes in "
        "military_retirement_pay instead. The model marks anyone with "
        "veterans_benefits as a veteran (is_veteran), so set is_veteran to "
        "false for a survivor or dependent whose VA payments go here."
    )
    definition_period = YEAR
    uprating = "gov.ssa.uprating"
    reference = (
        "https://www.law.cornell.edu/uscode/text/38/5301#a_1",
        "https://www.law.cornell.edu/uscode/text/10/1413a",
        "https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=19",
        "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=3",
    )
