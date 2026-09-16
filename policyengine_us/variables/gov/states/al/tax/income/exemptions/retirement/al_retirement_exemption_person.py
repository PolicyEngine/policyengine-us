from policyengine_us.model_api import *


class al_retirement_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Alabama retirement exemption for each person"
    unit = USD
    # Alabama Schedule RS Part II & III Line 10, Alabama Form 40 Booklet Page 14 Pension & Annuities, Alabama Section 40-18-19 (a)(13)
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1",
        "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23f40bk.pdf#page=14",
        "https://law.justia.com/codes/alabama/title-40/chapter-18/article-1/section-40-18-19/",
    )
    definition_period = YEAR
    defined_for = "al_retirement_exemption_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.tax.income.exemptions.retirement
        # Ala. Code § 40-18-19(a)(13) exempts up to $6,000 of taxable defined benefit retirement
        # distributions. Public pensions (TRS, ERS, federal civil service) are fully exempt
        # under § 40-18-19(a)(1), (2), (5), (6) via agi/deductions.yaml and do not consume this cap.
        retirement_income = add(
            person,
            period,
            [
                "taxable_retirement_distributions",
                "taxable_private_pension_income",
                "taxable_roth_conversions",
            ],
        )
        return min_(retirement_income, p.cap)
