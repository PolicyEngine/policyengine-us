from policyengine_us.model_api import *


class self_employment_tax_ald_person(Variable):
    value_type = float
    entity = Person
    label = "Self-employment tax ALD deduction for each person"
    unit = USD
    documentation = "Personal above-the-line deduction for self-employment tax"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164#f"

    def formula(person, period, parameters):
        self_employment_tax = person("self_employment_tax", period)
        is_dependent = person("is_tax_unit_dependent", period)
        total_tax = self_employment_tax * ~is_dependent
        percent_deductible = parameters(
            period
        ).gov.irs.ald.self_employment_tax.percent_deductible
        return total_tax * percent_deductible
