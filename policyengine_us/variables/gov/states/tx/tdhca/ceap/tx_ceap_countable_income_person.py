from policyengine_us.model_api import *


class tx_ceap_countable_income_person(Variable):
    value_type = float
    entity = Person
    label = "Texas Comprehensive Energy Assistance Program (CEAP) countable income for this person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.tdhca.texas.gov/sites/default/files/community-affairs/docs/26-LIHEAP-Plan-Amend1.pdf#page=8",
        "https://www.law.cornell.edu/regulations/texas/10-Tex-Admin-Code-SS-6-4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.ceap.income
        total = add(person, period, p.sources)
        age = person("age", period)
        return total * (age >= p.age_threshold)
