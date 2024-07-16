from policyengine_us.model_api import *


class va_personal_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia personal exemption for each person"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )

    def formula(person, period, parameters):
        return parameters(period).gov.states.va.tax.income.exemptions.personal
