from policyengine_us.model_api import *


class employer_federal_unemployment_tax(Variable):
    value_type = float
    entity = Person
    label = "Employer federal unemployment tax"
    documentation = (
        "Employer liability under the Federal Unemployment Tax Act (FUTA), "
        "including any state credit reduction."
    )
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        return person("employer_federal_unemployment_tax_rate", period) * person(
            "taxable_earnings_for_federal_unemployment_tax", period
        )
