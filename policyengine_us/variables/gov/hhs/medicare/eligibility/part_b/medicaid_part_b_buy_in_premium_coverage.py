from policyengine_us.model_api import *


class medicaid_part_b_buy_in_premium_coverage(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Part B premium paid by a state Medicaid buy-in for SSI recipients"
    definition_period = YEAR
    defined_for = "medicare_part_b_enrolled"
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395v#d",
        "https://www.ecfr.gov/current/title-42/section-407.40#p-407.40(c)(5)",
        "https://www.ecfr.gov/current/title-42/section-407.42#p-407.42(b)(1)(i)",
        "https://www.ecfr.gov/current/title-42/section-408.28",
        "https://secure.ssa.gov/poms.nsf/lnx/0600815001",
    )
    documentation = (
        "Annual standard Part B premium a state pays under its Part B buy-in "
        "agreement for an enrollee who has Medicaid as an SSI recipient, "
        "counted month by month in the months the person receives SSI. "
        "Medicare Savings Program coverage is msp_part_b_premium_coverage. "
        "SSI recipients in Section 1634 and SSI-criteria states are covered, "
        "and so are SSI recipients who qualify for Medicaid under a Section "
        "209(b) state's more restrictive criteria, since 42 CFR "
        "407.42(b)(1)(i) includes SSI recipients covered as categorically "
        "needy. Other full-benefit Medicaid groups, such as the medically "
        "needy, are not covered here: whether a state's buy-in agreement "
        "includes them varies by state. As with Medicare Savings Program "
        "coverage, any income-related monthly adjustment amount stays with "
        "the enrollee."
    )

    def formula(person, period, parameters):
        # The Section 1634 and SSI-criteria test of is_ssi_recipient_for_medicaid.
        state = person.household("state_code_str", period)
        categories = parameters(period).gov.hhs.medicaid.eligibility.categories
        is_covered = categories.ssi_recipient.is_covered[state].astype(bool)
        classified = person("medicaid_ssi_recipient_state_classification", period)
        classifications = classified.possible_values
        covered_classification = (classified == classifications.SECTION_1634) | (
            classified == classifications.SSI_CRITERIA
        )
        # The Section 209(b) test reads Medicaid countable income and
        # medically needy expenses, which count the premium before this
        # buy-in (medicare_part_b_premium_before_buy_in), so there is no cycle.
        # It tests eligibility, with no take-up step.
        ssi_medicaid_state = (is_covered & covered_classification) | person(
            "is_209b_ssi_recipient_for_medicaid", period
        )
        # 42 USC 1395v(d)(2)(C) and (d)(3)(A): buy-in coverage runs month by
        # month while the person receives SSI.
        monthly_premium = person("base_part_b_premium", period) / MONTHS_IN_YEAR
        coverage = 0
        for month in period.get_subperiods(MONTH):
            receives_ssi = (person("ssi", month) > 0) | person("receives_ssi", month)
            covered = receives_ssi & ssi_medicaid_state
            coverage += where(covered, monthly_premium, 0)
        return coverage
