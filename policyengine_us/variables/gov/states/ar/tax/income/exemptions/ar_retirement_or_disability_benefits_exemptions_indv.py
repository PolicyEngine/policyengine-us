from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemptions_indv(Variable):
    value_type = float
    entity = Person
    label = "Arkansas individual exemption for retirement or disability benefits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = "ar_retirement_or_disability_benefits_exemptions"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        head_eligibility = ((person("is_tax_unit_head", period)) & (person("age", period) >= p.age_threshold)).astype(int)
        print(head_eligibility)
        spouse_eligibility = ((person("is_tax_unit_spouse", period)) & (person("age", period) >= p.age_threshold)).astype(int)
        #print(spouse_eligibility)
        head_or_spouse_eligible = head_eligibility | spouse_eligibility
        #print(head_or_spouse_eligible)
        head_taxable_pension_income = person("taxable_pension_income", period) * head_or_spouse_eligible
        #print(head_taxable_pension_income)
        return min_(head_taxable_pension_income, p.amount)



