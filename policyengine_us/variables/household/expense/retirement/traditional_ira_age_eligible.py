from policyengine_us.model_api import *


class traditional_ira_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets the traditional IRA contribution age restriction"
    reference = (
        "https://www.irs.gov/pub/irs-prior/p590a--2017.pdf#page=5",
        # PDF pages 616-617: repeal of section 219(d)(1), effective after 2019.
        "https://www.govinfo.gov/content/pkg/PLAW-116publ94/pdf/PLAW-116publ94.pdf#page=616",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions.limit
        return person("age", period) < p.traditional_ira_age
