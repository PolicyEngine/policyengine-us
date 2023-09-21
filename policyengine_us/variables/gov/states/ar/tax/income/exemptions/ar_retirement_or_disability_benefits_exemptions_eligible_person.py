from policyengine_us.model_api import *


class ar_retirement_or_disability_benefits_exemptions_eligible_person(
    Variable
):
    value_type = float
    entity = Person
    label = "Arkansas individual retirement or disability benefits exemption eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits

        head_eligibility = (
            (person("is_tax_unit_head", period))
            & (person("age", period) >= p.age_threshold)
        ).astype(int)
        spouse_eligibility = (
            (person("is_tax_unit_spouse", period))
            & (person("age", period) >= p.age_threshold)
        ).astype(int)
        head_or_spouse_eligible = head_eligibility | spouse_eligibility

        return head_or_spouse_eligible
