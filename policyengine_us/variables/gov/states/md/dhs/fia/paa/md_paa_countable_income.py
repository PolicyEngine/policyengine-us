from policyengine_us.model_api import *

DAYS_IN_MONTH = 30


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
        # PAA Manual §900.3 / COMAR 07.03.07.08(B): MDH Rehabilitative
        # Residence customers receive a cost-of-care disregard up to the
        # per-diem ceiling ($54/day × ~30 days). Post-disregard income above
        # that ceiling counts against the personal needs allowance; income
        # below the ceiling produces zero countable income.
        countable_earned = person("md_paa_countable_earned_income", period)
        countable_unearned = person("md_paa_countable_unearned_income", period)
        post_disregard_income = countable_earned + countable_unearned
        living_arrangement = person("md_paa_living_arrangement", period)
        is_rehab = (
            living_arrangement == living_arrangement.possible_values.REHAB_RESIDENCE
        )
        per_diem = parameters(
            period
        ).gov.states.md.dhs.fia.paa.rehab_residence.cost_of_need_per_diem
        cost_of_need_ceiling = per_diem * DAYS_IN_MONTH
        rehab_countable = max_(post_disregard_income - cost_of_need_ceiling, 0)
        return where(is_rehab, rehab_countable, post_disregard_income)
