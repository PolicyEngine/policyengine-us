from policyengine_us.model_api import *


class al_retirement_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Alabama retirement exemption for each person"
    unit = USD
    # The Code of Alabama Section 40-18-19 (a)(13).
    documentation = "https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally"
    definition_period = YEAR
    defined_for = "al_retirement_exemption_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        retirement_income = add(
            person,
            period,
            [
                "taxable_retirement_distributions", "taxable_pension_income"]
                "taxable_401k_distributions",
                "taxable_sep_distributions",
                "taxable_403b_distributions",
                "keogh_distributions",
                "taxable_pension_income",
            ],
        )
        return min_(retirement_income, p.cap)
