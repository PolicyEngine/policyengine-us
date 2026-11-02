from policyengine_us.model_api import *


class medicaid_part_b_buy_in_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part B premium paid by a state Medicaid buy-in for SSI recipients"
    definition_period = YEAR
    defined_for = "medicare_part_b_enrolled"
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395v",
        "https://www.law.cornell.edu/cfr/text/42/part-407/subpart-C",
    )
    documentation = (
        "Annual standard Part B premium a state pays under its Part B buy-in "
        "agreement for an enrollee who has Medicaid as an SSI recipient in a "
        "Section 1634 or SSI-criteria state. "
        "Medicare Savings Program coverage is msp_part_b_premium_coverage. "
        "SSI recipients in Section 209(b) states and other full-benefit "
        "Medicaid groups, such as the medically needy, are not covered here: "
        "their Medicaid tests deduct this premium, and whether a state's "
        "buy-in agreement includes them varies by state. As with Medicare Savings Program coverage, any "
        "income-related monthly adjustment amount stays with the enrollee."
    )

    def formula(person, period, parameters):
        # The Section 1634 and SSI-criteria test of is_ssi_recipient_for_medicaid.
        # Its Section 209(b) branch is left out: that branch reads the
        # optional senior or disabled countable income, which deducts this
        # premium.
        state = person.household("state_code_str", period)
        categories = parameters(period).gov.hhs.medicaid.eligibility.categories
        is_covered = categories.ssi_recipient.is_covered[state].astype(bool)
        classified = person("medicaid_ssi_recipient_state_classification", period)
        classifications = classified.possible_values
        covered_classification = (classified == classifications.SECTION_1634) | (
            classified == classifications.SSI_CRITERIA
        )
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )
        ssi_medicaid = receives_ssi & is_covered & covered_classification
        return ssi_medicaid * person("base_part_b_premium", period)
