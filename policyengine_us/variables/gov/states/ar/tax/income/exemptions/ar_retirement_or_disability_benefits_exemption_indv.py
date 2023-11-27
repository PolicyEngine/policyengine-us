from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemption_indv(Variable):
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
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_person = person(
            "ar_retirement_or_disability_benefits_exemption_eligible_person",
            period,
        )
        pension_income = (
            person("taxable_pension_income", period) * head_or_spouse
        )
        # Filers over a certain age can deduct IRA distributions in addition to pension income
        regular_ira_distributions = (
            person("regular_ira_distributions", period) * eligible_person
        )
        eligible_pension_income = pension_income + regular_ira_distributions
        military_retirement_exemption = person(
            "ar_military_retirement_exemption", period
        )
        capped_exemption = max_(
            eligible_pension_income, military_retirement_exemption
        )
        return min_(capped_exemption, p.cap)
