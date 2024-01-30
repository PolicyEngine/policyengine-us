from policyengine_us.model_api import *


class va_aged_blind_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia aged/blind exemption for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.exemptions
        aged_person = person("is_irs_aged", period).astype(int)
        blind_person = person("is_blind", period).astype(int)
        aged_blind_count = aged_person + blind_person
        return aged_blind_count * p.aged_blind
