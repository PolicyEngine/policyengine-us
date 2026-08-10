from policyengine_us.model_api import *


class is_209b_ssi_recipient_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "209(b) SSI recipients"
    documentation = (
        "Whether this SSI recipient qualifies for Medicaid through a "
        "Section 209(b) state's more restrictive aged, blind, or disabled "
        "criteria."
    )
    definition_period = YEAR
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010",
        "https://www.medicaid.gov/resources-for-states/downloads/macpro-ig-more-restrictive-requirements-1902f-209bstates.pdf#page=3",
        "https://www.govinfo.gov/link/cfr/42/435?link-type=pdf&sectionnum=121&year=mostrecent",
    )

    def formula(person, period, parameters):
        classified = person("medicaid_ssi_recipient_state_classification", period)
        is_209b_state = classified == classified.possible_values.SECTION_209B
        receives_ssi = (person("ssi", period) > 0) | (
            add(person, period, ["receives_ssi"]) > 0
        )

        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.ssi_recipient.section_209b
        is_excluded_nonblind_child = (
            p.excludes_nonblind_disabled_children[state].astype(bool)
            & person("is_child", period)
            & ~person("is_blind", period)
        )

        return (
            receives_ssi
            & is_209b_state
            & ~is_excluded_nonblind_child
            & person("is_209b_ssi_recipient_income_eligible_for_medicaid", period)
            & person("is_optional_senior_or_disabled_asset_eligible", period)
        )
