from policyengine_us.model_api import *


class me_ssp_couple(Variable):
    value_type = float
    entity = Person
    label = "Maine SSP per-person share of the couple monthly amount"
    unit = USD
    definition_period = MONTH
    defined_for = "me_ssp_eligible"
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ssp
        category = person("me_ssp_payment_category", period)
        categories = category.possible_values
        # Couple totals for D/E/F/G are facility rates, not 2x individual.
        # Split 50/50 per person; ssa/ssi splits couple income the same way.
        per_person_share = p.amount.couple[category] / 2
        is_fixed = (
            (category == categories.LIVING_ALONE_OR_WITH_OTHERS)
            | (category == categories.HOUSEHOLD_OF_ANOTHER)
            | (category == categories.MEDICAID_FACILITY)
            | (category == categories.RESIDENTIAL_CARE_FACILITY)
        )
        # SS-only path: apply Maine's couple disregard ($80 for A/C/H/I,
        # $0 for D/E/F/G) per Part 7 §4.1, split 50/50 per person.
        federal_excess = max_(0, -person("uncapped_ssi", period))
        per_person_disregard = p.disregard.couple[category] / 2
        adjusted_excess = max_(0, federal_excess - per_person_disregard)
        within_limit = adjusted_excess <= per_person_share
        return where(
            is_fixed,
            per_person_share * within_limit,
            max_(0, per_person_share - adjusted_excess),
        )
