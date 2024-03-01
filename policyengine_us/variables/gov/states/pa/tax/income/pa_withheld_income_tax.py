from policyengine_us.model_api import *


class pa_withheld_income_tax(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania withheld income tax"
    defined_for = StateCode.PA
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        employment_income = person("irs_employment_income", period)
        p = parameters(period).gov.states.pa.tax.income
