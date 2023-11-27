from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Arkansas individual retirement or disability benefits exemption"
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        age_eligible = person("age", period) >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse & age_eligible
