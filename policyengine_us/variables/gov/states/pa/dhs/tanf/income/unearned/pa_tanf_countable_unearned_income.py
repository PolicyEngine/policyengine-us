from policyengine_us.model_api import *


class pa_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.98 - Deductions from unearned income"
    documentation = "Countable unearned income after applicable deductions per Section 183.98. For initial implementation, this equals gross unearned income as specific deductions are not yet implemented. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.98.html"

    def formula(person, period, parameters):
        # For initial implementation, countable unearned income equals gross
        # Future enhancement: implement specific unearned income deductions per § 183.98
        gross_unearned = person("pa_tanf_gross_unearned_income", period)

        return gross_unearned
