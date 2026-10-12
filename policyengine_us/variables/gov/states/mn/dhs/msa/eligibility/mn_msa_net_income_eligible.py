from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class mn_msa_net_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Minnesota Supplemental Aid net income eligible"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Countable-income logic intentionally duplicates mn_msa_person to
        # avoid a defined_for cycle (mn_msa_person is gated on
        # mn_msa_eligible_person, which depends on this variable). Keep the
        # two formulas in sync when changing income treatment.
        # Per House Research Oct 2024 p.3 and CM 0018.18: for SSI recipients,
        # MSA's net-income calc counts the full federal SSI FBR as gross
        # unearned income and applies only the $20 general disregard
        # (federal SSI already consumed the $65 + 1/2 earned disregards).
        # Non-SSI track recipients get the standard $20 + $65 + 1/2
        # disregards on actual earned and unearned income.
        # FLA-D recipients are exempt from the $20 disregard so the formula
        # collapses to FBR + unearned vs PNA.
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        is_medicaid_facility = arrangement == LA.MEDICAID_FACILITY
        ssi = person("ssi", period)
        receives_ssi = ssi > 0
        ssi_fbr = person("ssi_amount_if_eligible", period)
        p = parameters(period).gov.ssa.ssi.income.exclusions
        disregard = where(is_medicaid_facility, 0, p.general)
        raw_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )

        # SSI track: count FBR as unearned, apply $20 once at AU level for
        # couples (matches mn_msa_person.py SSI track formula).
        couple_ssi_countable = max_(
            person.marital_unit.sum(ssi_fbr)
            + person.marital_unit.sum(raw_unearned)
            - disregard,
            0,
        )
        individual_ssi_countable = max_(ssi_fbr + raw_unearned - disregard, 0)
        ssi_countable = where(is_couple, couple_ssi_countable, individual_ssi_countable)

        # Non-SSI track: federal $20 + $65 + 1/2 disregards on actual
        # earned and unearned. _apply_ssi_exclusions takes annual amounts
        # and returns annual countable; convert to monthly.
        annual_earned = add(
            person,
            period.this_year,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        annual_unearned = add(
            person,
            period.this_year,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        couple_earned = person.marital_unit.sum(annual_earned)
        couple_unearned = person.marital_unit.sum(annual_unearned)
        couple_non_ssi_countable = (
            _apply_ssi_exclusions(couple_earned, couple_unearned, parameters, period)
            / MONTHS_IN_YEAR
        )
        individual_non_ssi_countable = (
            _apply_ssi_exclusions(annual_earned, annual_unearned, parameters, period)
            / MONTHS_IN_YEAR
        )
        non_ssi_countable = where(
            is_couple, couple_non_ssi_countable, individual_non_ssi_countable
        )

        # For couples both ssi_countable and non_ssi_countable are already
        # AU-aggregate (computed via marital_unit.sum); the couple standard
        # is the AU total, so compare directly.
        countable = where(receives_ssi, ssi_countable, non_ssi_countable)
        special_needs = person("mn_msa_special_needs_total", period)
        need_standard = person("mn_msa_assistance_standard", period) + where(
            is_couple, person.marital_unit.sum(special_needs), special_needs
        )
        return countable <= need_standard
