from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemptions_indv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas individual retirement or disability benefits exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = (
        "ar_retirement_or_disability_benefits_exemptions_eligible_person"
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        head_or_spouse_eligible = person(
            "ar_retirement_or_disability_benefits_exemptions_eligible_person",
            period,
        )
        head_taxable_pension_income = (
            person("taxable_pension_income", period) * head_or_spouse_eligible
        )
        return min_(head_taxable_pension_income, p.amount)
