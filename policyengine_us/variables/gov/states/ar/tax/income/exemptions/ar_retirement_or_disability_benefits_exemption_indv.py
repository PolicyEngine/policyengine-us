from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemption_indv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas individual retirement or disability benefits exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = (
        "ar_retirement_or_disability_benefits_exemption_eligible_person"
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        eligible_person = person(
            "ar_retirement_or_disability_benefits_exemption_eligible_person",
            period,
        )
        pension_income = person("taxable_pension_income", period) + person(
            "pension_contributions", period
        )
        eligible_pension_income = pension_income * eligible_person
        return min_(eligible_pension_income, p.amount)
