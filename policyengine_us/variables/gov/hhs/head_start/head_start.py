from policyengine_us.model_api import *


class head_start(Variable):
    value_type = float
    entity = Person
    label = "Amount of Head Start benefit"
    definition_period = YEAR
    defined_for = "is_head_start_eligible"
    reference = "https://headstart.gov/program-data/article/head-start-program-facts-fiscal-year-2022"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.head_start
        state = person.household("state_code_str", period)
        spending = p.spending[state]
        enrollment = p.enrollment[state]
        mask = enrollment > 0
        result = np.zeros_like(p.spending[state])
        result[mask] = spending[mask] / enrollment[mask]
        return result
