from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
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
        earned = person("ssi_marital_earned_income", period)
        student_exclusion = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        adjusted_earned = max_(earned - student_exclusion, 0)
        unearned = add(
            person,
            period,
            [
                "ssi_marital_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_parent",
                "ssi_in_kind_support_and_maintenance",
            ],
        )
        personal_countable = _apply_ssi_exclusions(
            adjusted_earned,
            unearned,
            parameters,
            period,
        )

        both_eligible = person("ssi_couple_computation_applies", period.this_year)
        # COMAR 07.03.07.07 counts the individual's own income and has no
        # spousal deeming. The SSI cascade deems spouse income only to people
        # SSA can pay, so people who fail SSI's citizen or qualified-noncitizen
        # test count their own income alone.
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
