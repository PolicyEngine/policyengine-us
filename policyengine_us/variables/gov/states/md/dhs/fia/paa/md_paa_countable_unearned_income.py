from policyengine_us.model_api import *


class md_paa_countable_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20500%20Financial%20Eligibility%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-09",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.dhs.fia.paa.income
        unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        return max_(unearned - p.unearned_income_disregard, 0)
