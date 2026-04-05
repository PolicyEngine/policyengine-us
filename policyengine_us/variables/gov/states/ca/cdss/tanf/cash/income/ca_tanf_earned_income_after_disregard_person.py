from policyengine_us.model_api import *


class ca_tanf_earned_income_after_disregard_person(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "California CalWORKs earned income after applicant disregard per person"
    unit = USD
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11450.12."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.cdss.tanf.cash.income.disregards.applicant
        earned = person("ca_tanf_earned_income_person", period)
        return max_(earned - p.flat, 0)
