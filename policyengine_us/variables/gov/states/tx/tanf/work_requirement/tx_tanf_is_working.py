from policyengine_us.model_api import *


class tx_tanf_is_working(Variable):
    value_type = bool
    entity = Person
    label = "Person is working for Texas TANF work requirements"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/e-100-participation-texas-works-program",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-1405",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        return (employment_income > 0) | (self_employment_income > 0)
