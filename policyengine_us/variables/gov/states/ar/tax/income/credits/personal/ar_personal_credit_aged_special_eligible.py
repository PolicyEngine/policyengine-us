from policyengine_us.model_api import *


class ar_personal_credit_aged_special_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Arkansas eligibility for aged special personal credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1"
        "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12"
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.ar.tax.income.credits.personal
        aged_person = age >= p.aged.age_threshold

        disability_exemption_eligible = (
            person(
                "ar_retirement_or_disability_benefits_exemptions_indv", period
            )
            == 0
        )
        return aged_person & disability_exemption_eligible
