from policyengine_us.model_api import *


class medicaid_parent_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid parent income limit"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.110",
        "https://www.dmas.virginia.gov/media/0aynyhxk/m04-1-1-26a.pdf#page=51",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        va_lifc = parameters(period).gov.states.va.dmas.medicaid.lifc
        state = person.household("state_code_str", period)
        state_code = person.household("state_code", period)
        if va_lifc.in_effect:
            return where(
                state_code == StateCode.VA,
                person("va_medicaid_lifc_income_limit", period),
                p.income_limit[state],
            )
        return p.income_limit[state]
