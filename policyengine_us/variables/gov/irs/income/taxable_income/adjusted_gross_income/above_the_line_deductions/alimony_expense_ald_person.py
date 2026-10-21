from policyengine_us.model_api import *


class alimony_expense_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Alimony expense ALD for each person"
    unit = USD
    documentation = (
        "The alimony each person pays under a divorce or separation instrument "
        "executed before 2019, which they deduct on their own return. "
        "alimony_expense_ald adds the head's and spouse's amounts for the tax "
        "unit's return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/215",
        "https://www.irs.gov/taxtopics/tc452",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.ald.alimony_expense
        eligible = p.divorce_year_threshold.calc(person("divorce_year", period))
        return person("alimony_expense", period) * eligible
