from policyengine_us.model_api import *


class al_retirement_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Alabama retirement exemption"
    # Alabama Schedule RS Part II & III Line 10, Alabama Form 40 Booklet Page 14 Pension & Annuities, Alabama Legal Code Section 40-18-19 (a)(13)
    documentation = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1"
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2024/01/23f40bk.pdf#page=14"
        "https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally"
    )
    definition_period = YEAR
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        age = person("age", period)
        eligible_age = age >= p.age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eligible_age & head_or_spouse
