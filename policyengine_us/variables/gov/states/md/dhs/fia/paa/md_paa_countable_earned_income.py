from policyengine_us.model_api import *


class md_paa_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20500%20Financial%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-08",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.dhs.fia.paa.income
        earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        leftover_general = max_(p.unearned_income_disregard - unearned, 0)
        effective_earned_disregard = (
            p.earned_income_disregard.initial + leftover_general
        )
        earned_after_disregard = max_(earned - effective_earned_disregard, 0)
        return earned_after_disregard * (1 - p.earned_income_disregard.rate)
