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
        # Only head or spouse of the tax unit will have this exemption
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disability_benefits_and_taxable_pensions = add(
            person, period, ["disability_benefits", "taxable_pension_income"]
        )
        # Filers over a certain age can deduct IRA distributions in addition to pension income
        ira_age_eligible = person("age", period) >= p.age_threshold
        age_eligible_ira_distributions = ira_age_eligible * person(
            "taxable_ira_distributions", period
        )
        return head_or_spouse * (
            disability_benefits_and_taxable_pensions
            + age_eligible_ira_distributions
        )
