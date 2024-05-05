from policyengine_us.model_api import *


class ar_capped_retirement_or_disability_benefits_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Arkansas capped individual retirement or disability benefits exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=13"
    defined_for = "ar_retirement_or_disability_benefits_exemption_person"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.exemptions.retirement_or_disability_benefits
        eligible_pension_income = person(
            "ar_retirement_or_disability_benefits_exemption_person", period
        )
        military_retirement_exemption = person(
            "ar_military_retirement_income_person", period
        )
        larger_exemption = max_(
            eligible_pension_income, military_retirement_exemption
        )
        return min_(larger_exemption, p.cap)
