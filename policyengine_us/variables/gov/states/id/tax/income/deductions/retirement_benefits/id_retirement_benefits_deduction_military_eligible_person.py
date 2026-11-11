from policyengine_us.model_api import *


class id_retirement_benefits_deduction_military_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Idaho retirement benefits deduction on military retirement benefits"
    documentation = """
    Idaho Code 63-3022A(1)(b) lets a retired member of the military, or the
    member's unremarried widow or widower, count military retirement benefits
    toward the retirement benefits deduction if the recipient is classified
    as disabled, has reached age 62 by the end of the tax year, or was
    employed during the tax year with enough income from that employment to
    have to file a federal return. Before 2025 these benefits had the age test
    of the other retirement benefits in 63-3022A(1): age 65, or age 62 and
    classified as disabled. The age parameters carry both rules.
    """
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://legislature.idaho.gov/wp-content/uploads/sessioninfo/2025/legislation/H0040.pdf#page=5",
        "https://legislature.idaho.gov/wp-content/uploads/sessioninfo/2025/legislation/H0479.pdf#page=2",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits.military
        age_threshold = where(
            person("is_disabled", period),
            p.age_eligibility.disabled,
            p.age_eligibility.main,
        )
        age_eligible = person("age", period) >= age_threshold
        employment_eligible = person(
            "id_retirement_benefits_deduction_military_employment_eligible", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse & (age_eligible | employment_eligible)
