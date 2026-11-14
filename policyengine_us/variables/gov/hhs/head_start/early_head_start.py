from policyengine_us.model_api import *


class early_head_start(Variable):
    value_type = float
    entity = Person
    label = "Early Head Start"
    unit = USD
    definition_period = YEAR
    defined_for = "is_early_head_start_eligible"
    documentation = (
        "State Early Head Start spending per enrolled child, for the months of "
        "the year the child's eligibility covers "
        "(head_start_qualifying_months)."
    )
    reference = (
        "https://headstart.gov/program-data/article/head-start-program-facts-fiscal-year-2022",
        "https://www.ecfr.gov/current/title-45/section-1302.12#p-1302.12(j)",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.head_start.early_head_start
        state = person.household("state_code_str", period)
        spending = p.spending[state]
        enrollment = p.enrollment[state]
        mask = enrollment > 0
        result = np.zeros_like(p.spending[state])
        result[mask] = spending[mask] / enrollment[mask]
        takes_up = person("takes_up_early_head_start_if_eligible", period)
        months = person("head_start_qualifying_months", period)
        return result * takes_up * months / MONTHS_IN_YEAR
