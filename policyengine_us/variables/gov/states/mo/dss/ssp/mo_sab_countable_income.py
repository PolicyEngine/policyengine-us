from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class mo_sab_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri SAB countable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MO
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=2",
    )

    def formula(person, period, parameters):
        # SAB applies SSI-methodology exclusions ($20 general, $65 earned,
        # 50% of remainder) per 13 CSR 40-2.120(3), but the income test is
        # applied to all blind applicants — including those who would fail
        # federal SSI on resources or immigration. Using ssi_countable_income
        # here would zero out for non-eligibles and silently bypass the SAB
        # income test. Appendix K p.5 specifies the test is calculated
        # individually, regardless of marital status, so we use individual
        # (not marital) earned/unearned variables and do not apply the
        # couple-computation divide-by-2.
        earned = person("ssi_earned_income", period)
        student_exclusion = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        adjusted_earned = max_(earned - student_exclusion, 0)
        # ISM (in-kind support and maintenance) is counted as unearned per
        # 20 CFR § 416.1140 and is independent of SSI eligibility.
        # Parent deeming (20 CFR § 416.1165) is not included because SAB is
        # an 18+ program and the variable is gated on is_child.
        unearned = person("ssi_unearned_income", period)
        ism = person("ssi_in_kind_support_and_maintenance", period)
        total_unearned = unearned + ism
        own_countable = _apply_ssi_exclusions(
            adjusted_earned, total_unearned, parameters, period
        )
        # Spousal deeming from an SSI-ineligible spouse (20 CFR § 416.1163)
        # applies for SAB applicants who are themselves SSI-eligible. The
        # underlying variable is gated on is_ssi_eligible_individual, so SAB
        # applicants who fail federal SSI on resources or immigration won't
        # get spousal deeming captured here — a narrow modeling limitation.
        spousal_deemed = person("ssi_income_deemed_from_ineligible_spouse", period)
        return own_countable + spousal_deemed
