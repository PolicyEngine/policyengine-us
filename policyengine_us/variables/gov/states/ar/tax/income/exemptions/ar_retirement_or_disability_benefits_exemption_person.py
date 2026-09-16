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
        p_irs = parameters(period).gov.irs.income.exemption.traditional_distribution
        p_ar = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        # Only head or spouse of the tax unit will have this exemption
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        employment_retirement_and_disability = add(
            person, period, p_ar.employment_sources
        )
        # Filers over a certain age can deduct IRA distributions in addition to pension income
        ira_age_eligible = person("age", period) >= p_irs.age_threshold
        age_eligible_ira_distributions = ira_age_eligible * person(
            "taxable_ira_distributions", period
        )
        return head_or_spouse * (
            employment_retirement_and_disability + age_eligible_ira_distributions
        )
