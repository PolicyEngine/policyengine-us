from policyengine_us.model_api import *


class md_paa_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable income"
    unit = USD
    definition_period = MONTH
    defined_for = "md_paa_eligible"
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
        "https://www.law.cornell.edu/regulations/maryland/COMAR-07-03-07-08",
    )

    def formula(person, period, parameters):
        # Per COMAR 07.03.07.08(B), residents of MDH Rehabilitative Residences
        # have a cost-of-care disregard. MDH pays the cost of care directly, so
        # PAA contributes only the personal needs allowance — countable income
        # is fully disregarded.
        living_arrangement = person("md_paa_living_arrangement", period)
        is_rehab = (
            living_arrangement == living_arrangement.possible_values.REHAB_RESIDENCE
        )
        countable_earned = person("md_paa_countable_earned_income", period)
        countable_unearned = person("md_paa_countable_unearned_income", period)
        return where(is_rehab, 0, countable_earned + countable_unearned)
