from policyengine_us.model_api import *


class pr_veteran_exemption(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico veteran exemption"
    reference = "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR

    def formula(person, period, parameters):
        # line 9
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.exemptions
        vet_status = person("is_veteran", period)
        return vet_status * p.veteran
