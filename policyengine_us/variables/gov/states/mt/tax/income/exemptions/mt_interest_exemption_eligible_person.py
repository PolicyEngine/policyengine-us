from policyengine_us.model_api import *


class mt_interest_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Montana interest exemption"
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/Form-2-2022-Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions.interest
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period)
        return person.tax_unit.any(age >= p.age_threshold) & head_or_spouse
