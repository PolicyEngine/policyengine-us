from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas individual retirement or disability benefits exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.income.exemption.traditional_distribution
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        pension_income = (
            person("taxable_pension_income", period) * head_or_spouse
        )
        # Filers over a certain age can deduct IRA distributions in addition to pension income
        eligible_person = head_or_spouse & (
            person("age", period) >= p.age_threshold
        )
        eligible_ira_distributions = (
            person("regular_ira_distributions", period) * eligible_person
        )
        return pension_income + eligible_ira_distributions
