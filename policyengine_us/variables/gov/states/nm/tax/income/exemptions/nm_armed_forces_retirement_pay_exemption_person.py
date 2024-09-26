from policyengine_us.model_api import *


class nm_armed_forces_retirement_pay_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "New Mexico armed forces retirement pay exemption per person "
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-513-effective-until-112025-exemption-armed-forces-retirement-pay"
    defined_for = StateCode.NM

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.armed_forces_retirement_pay
        armed_forces_retirement_pay = person("military_retirement_pay", period)
        capped_amount = min_(armed_forces_retirement_pay, p.cap)
        qualifies = person("is_tax_unit_head_or_spouse", period)
        return qualifies * capped_amount
