from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_income,
)


class md_paa_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Maryland PAA countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.07",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.08",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.09",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
    )

    def formula(person, period, parameters):
        # PAA mirrors the SSI $20 unearned / $65 earned / 50% earned
        # exclusions, but it must count income for every PAA eligibility
        # pathway. Using ssi_countable_income would zero out SSDI-only
        # recipients unless an input also marks them as SSI-disabled.
        # NOTE: this annual formula applies one couple status to the whole
        # year (both_eligible below), so it combines the spouses' annual
        # income by that same status. ssi_marital_earned_income and
        # ssi_marital_unearned_income are monthly and follow each month's
        # status; their annual totals would not match it in a year with a
        # part-year facility stay.
        earned = _ssi_couple_income(person, period, "ssi_earned_income")
        student_exclusion = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        adjusted_earned = max_(earned - student_exclusion, 0)
        unearned = (
            _ssi_couple_income(person, period, "ssi_unearned_income")
            + person("ssi_unearned_income_deemed_from_ineligible_parent", period)
            + person("ssi_in_kind_support_and_maintenance", period)
        )
        personal_countable = _apply_ssi_exclusions(
            adjusted_earned,
            unearned,
            parameters,
            period,
        )

        both_eligible = person("ssi_couple_computation_applies", period.this_year)
        # COMAR 07.03.07.07 counts the individual's own income and has no
        # spousal deeming, so people who fail SSI's citizen or
        # qualified-noncitizen test count their own income alone, including
        # those who report SSI receipt.
        # NOTE: for citizens and qualified noncitizens the SSI deemed amount is
        # still added, although their imputed SSI already reflects it. This
        # predates the noncitizen change and is a known limitation.
        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)
        meets_ssi_immigration_test = is_citizen | is_qualified_noncitizen
        spousal_deemed = where(
            meets_ssi_immigration_test,
            person("ssi_income_deemed_from_ineligible_spouse", period),
            0,
        )
        return where(
            both_eligible,
            personal_countable / 2,
            personal_countable + spousal_deemed,
        )
