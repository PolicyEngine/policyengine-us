from policyengine_us.model_api import *


class alimony_expense_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Alimony expense ALD for each person"
    unit = USD
    documentation = (
        "Each person's own above-the-line deduction for alimony paid under a "
        "divorce or separation instrument executed before 2019 (Schedule 1, "
        "line 19a), on that person's own return."
    )
    definition_period = YEAR
    reference = "https://www.irs.gov/taxtopics/tc452"

    def formula(person, period, parameters):
        divorce_year = person("divorce_year", period)
        alimony_expense = person("alimony_expense", period)
        p = parameters(period).gov.irs.ald.alimony_expense
        return alimony_expense * p.divorce_year_threshold.calc(divorce_year)
