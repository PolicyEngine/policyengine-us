from policyengine_us.model_api import *


class pa_nontaxable_pension_income(Variable):
    value_type = float
    entity = Person
    label = "Pension income taxable by US but not by PA"
    unit = USD
    documentation = "US taxable pension income excluded from PA AGI."
    definition_period = YEAR
    reference = "https://www.revenue.pa.gov/FormsandPublications/FormsforIndividuals/PIT/Documents/2021/2021_pa-40in.pdf#page=8"

    def formula(person, period, parameters):
        retired = person("is_retired", period)
        us_taxable_pension = person("taxable_pension_income", period)
        return where(retired, us_taxable_pension, 0)
