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
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.08",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.07.09",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20900%20Calculation%20of%20Benefits%20rev%2011.22.docx",
    )

    def formula(person, period, parameters):
        # PAA mirrors the SSI $20 unearned / $65 earned / 50% earned
        # exclusions, but it must count income for every PAA eligibility
        # pathway. Using ssi_countable_income would zero out SSDI-only
        # recipients unless an input also marks them as SSI-disabled.
        both_eligible = person("ssi_couple_computation_applies", period.this_year)
        # COMAR 07.03.07.08 sets earned-income deductions for an individual,
        # and DHS states that "The assistance unit is always one person." No
        # Maryland text adopts SSI's income computation or lets a spouse's
        # residual business loss reduce the applicant's earnings, as POMS SI
        # 00820.210 B.2.c does for SSI. Outside the couple computation, read
        # the applicant's own signed earnings; the floor below stops an own
        # residual loss from reducing unearned income.
        earned = where(
            both_eligible,
            person("ssi_marital_earned_income", period),
            person("ssi_earned_income", period),
        )
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

        spousal_deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
        return where(
            both_eligible,
            personal_countable / 2,
            personal_countable + spousal_deemed,
        )
