from policyengine_us.model_api import *


class is_optional_senior_or_disabled_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Seniors or disabled people not meeting SSI rules"
    documentation = "Whether this person qualifies for Medicaid through the State's optional aged, blind, or disabled pathway (not otherwise SSI-eligible)"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.law.cornell.edu/uscode/text/42/1396b#v",
        "https://www.ecfr.gov/current/title-42/section-435.406#p-435.406(b)",
    )

    def formula(person, period, parameters):
        # Some states cover aged, blind, or disabled people as categorically
        # needy only if they receive SSI, and have no group for those who do not.
        # Emergency Medicaid waives the SSI receipt requirement for noncitizens
        # who fail the Medicaid immigration test (42 U.S.C. 1396b(v)(2)(B);
        # 42 CFR 435.406(b) and 440.255(c)), so they stay in this group.
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        immigration_eligible = person("is_medicaid_immigration_status_eligible", period)
        covers_group = (
            p.covers_non_ssi_recipients[state].astype(bool) | ~immigration_eligible
        )
        # Arkansas's group (ARSeniors) covers only aged people. A blind or
        # disabled noncitizen who fails the immigration test would get
        # emergency Medicaid through the SSI group instead, so they keep this
        # group only if they meet SSI's income and resource tests.
        meets_ssi_income_test = person(
            "ssi_countable_income", period
        ) / MONTHS_IN_YEAR < person("ssi_amount_if_eligible", period.first_month)
        meets_ssi_resource_test = person("meets_ssi_resource_test", period.first_month)
        covers_blind_or_disabled = p.covers_blind_or_disabled[state].astype(bool) | (
            ~immigration_eligible & meets_ssi_income_test & meets_ssi_resource_test
        )
        is_senior_or_disabled = where(
            covers_blind_or_disabled,
            person("is_ssi_aged_blind_disabled", period),
            person("is_ssi_aged", period),
        )
        income_eligible = person(
            "is_optional_senior_or_disabled_income_eligible", period
        )
        asset_eligible = person("is_optional_senior_or_disabled_asset_eligible", period)
        return covers_group & is_senior_or_disabled & income_eligible & asset_eligible
