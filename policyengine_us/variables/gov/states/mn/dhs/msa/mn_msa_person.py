from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class mn_msa_person(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid per-person amount"
    unit = USD
    definition_period = MONTH
    defined_for = "mn_msa_eligible_person"
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # Countable-income logic intentionally duplicates
        # mn_msa_net_income_eligible to avoid a defined_for cycle (this
        # variable is gated on mn_msa_eligible_person, which depends on
        # mn_msa_net_income_eligible). Keep the two formulas in sync when
        # changing income treatment.
        # MSA inherits federal SSI's $20 / $65 / 1/2 disregards (CM 0018.18).
        # The SSI track substitutes the federal SSI FBR for the recipient's
        # post-disregard SSI payment so MSA tops up against the FBR rather
        # than the federal payment. FLA-D recipients are exempt from the $20
        # general disregard. Couples are computed at the marital unit then
        # split 50/50 to avoid wasting disregards on asymmetric income.
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        is_medicaid_facility = arrangement == LA.MEDICAID_FACILITY
        standard = person("mn_msa_assistance_standard", period)
        special_needs = person("mn_msa_special_needs_total", period)
        need_standard = standard + special_needs
        # Couple income is tested at the assistance-unit level, but modeled
        # special needs remain attached to the spouse with the allowance.
        couple_special_needs = person.marital_unit.sum(special_needs)
        special_needs_share = special_needs / max_(couple_special_needs, 1)
        ssi = person("ssi", period)
        receives_ssi = ssi > 0
        ssi_fbr = person("ssi_amount_if_eligible", period)
        p = parameters(period).gov.ssa.ssi.income.exclusions
        raw_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        disregard = where(is_medicaid_facility, 0, p.general)

        # SSI track: aggregate FBR + unearned at marital unit for couples,
        # apply $20 once, then split supplement 50/50.
        couple_ssi_countable = max_(
            person.marital_unit.sum(ssi_fbr)
            + person.marital_unit.sum(raw_unearned)
            - disregard,
            0,
        )
        couple_ssi_supplement = (
            max_(standard - couple_ssi_countable, 0) / 2
            + max_(couple_special_needs - max_(couple_ssi_countable - standard, 0), 0)
            * special_needs_share
        )
        individual_ssi_countable = max_(ssi_fbr + raw_unearned - disregard, 0)
        individual_ssi_supplement = max_(need_standard - individual_ssi_countable, 0)
        ssi_track = where(is_couple, couple_ssi_supplement, individual_ssi_supplement)

        # Non-SSI track: applies federal SSI exclusions ($20 + $65 + 1/2)
        # to raw earned and unearned income. Helper accepts annual amounts
        # and returns annual countable; convert to monthly to match MSA.
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
        couple_non_ssi_countable_annual = _apply_ssi_exclusions(
            couple_earned, couple_unearned, parameters, period
        )
        individual_non_ssi_countable_annual = _apply_ssi_exclusions(
            annual_earned, annual_unearned, parameters, period
        )
        couple_non_ssi_countable = couple_non_ssi_countable_annual / MONTHS_IN_YEAR
        individual_non_ssi_countable = (
            individual_non_ssi_countable_annual / MONTHS_IN_YEAR
        )
        couple_non_ssi_supplement = (
            max_(standard - couple_non_ssi_countable, 0) / 2
            + max_(
                couple_special_needs - max_(couple_non_ssi_countable - standard, 0), 0
            )
            * special_needs_share
        )
        individual_non_ssi_supplement = max_(
            need_standard - individual_non_ssi_countable, 0
        )
        non_ssi_track = where(
            is_couple, couple_non_ssi_supplement, individual_non_ssi_supplement
        )

        return where(receives_ssi, ssi_track, non_ssi_track)
