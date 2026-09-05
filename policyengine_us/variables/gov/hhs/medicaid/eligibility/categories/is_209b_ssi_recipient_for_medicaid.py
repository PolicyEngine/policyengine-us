from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


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
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0840-000-00/0840-010-00/0840-010-35/",
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
        # Some states screen the disability category for substantial
        # gainful activity. Input SSI receipt above SGA is treated as a
        # section 1619(a) continuation while SSI cash is still payable on
        # income alone, so the screen applies only past that point.
        is_sga_earner = person("ssi_engaged_in_sga", period) & ~person(
            "is_ssi_aged", period
        )
        # ssi_countable_income is zero for anyone the model does not find
        # SSI eligible, so apply the standard exclusions to the person's
        # own income directly.
        ssi_benefit_rate = add(person, period, ["ssi_amount_if_eligible"])
        own_countable_income = _apply_ssi_exclusions(
            person("ssi_earned_income", period),
            person("ssi_unearned_income", period),
            parameters,
            period,
        )
        would_receive_ssi_cash = ssi_benefit_rate > own_countable_income
        is_excluded_sga_earner = (
            p.applies_sga_screen[state].astype(bool)
            & is_sga_earner
            & ~would_receive_ssi_cash
        )

        return (
            receives_ssi
            & is_209b_state
            & ~is_excluded_nonblind_child
            & ~is_excluded_sga_earner
            & person("is_209b_ssi_recipient_income_eligible_for_medicaid", period)
            & person("is_optional_senior_or_disabled_asset_eligible", period)
        )
