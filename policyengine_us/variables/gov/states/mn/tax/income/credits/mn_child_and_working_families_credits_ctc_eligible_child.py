from policyengine_us.model_api import *


class mn_child_and_working_families_credits_ctc_eligible_child(Variable):
    value_type = float
    entity = Person
    label = "Minnesota child and working families credits child tax credit eligible child"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0661#stat.290.0661.4"
        "https://www.revisor.mn.gov/statutes/cite/290.0671"
        "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1cwfc-23_1.pdf"
    )
    defined_for = StateCode.MN

    def formula(person, period, parameters):
        age = person("age", period)
        meets_eitc_identification_requirements = person(
            "meets_eitc_identification_requirements", period
        )
        p = parameters(period).gov.states.mn.tax.income.credits.cwfc.ctc
        age_eligible = age < p.age_limit
        return age_eligible & meets_eitc_identification_requirements
