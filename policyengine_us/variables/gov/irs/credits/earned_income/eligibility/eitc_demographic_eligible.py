from policyengine_us.model_api import *


class eitc_demographic_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets demographic eligibility for EITC"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A",
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D",
        "https://www.congress.gov/117/bills/hr1319/BILLS-117hr1319enr.pdf#page=150",
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=18",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # IRC 32(c)(1)(A)(i): an individual who has a qualifying child is an
        # eligible individual. 32(c)(3)(D) and (m) leave a child without a
        # valid SSN out only of the amount under subsection (b), which
        # eitc_child_count carries. Since ARPA section 9622 struck former
        # (c)(1)(F) (from 2021), such a child still establishes eligibility,
        # so the filer gets the zero-child amount without the childless age
        # test. Years before 2021 keep the identification-filtered count.
        p = parameters(period).gov.irs.credits.eitc.eligibility
        has_child = tax_unit("eitc_child_count", period) > 0
        if not p.qualifying_child_without_identification_bar:
            has_child = has_child | tax_unit.any(
                person("is_eitc_qualifying_child", period)
            )
        age = person("age", period)
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        min_age_non_student = parameters.gov.irs.credits.eitc.eligibility.age.min(
            period
        )
        min_age_student = parameters.gov.irs.credits.eitc.eligibility.age.min_student(
            period
        )
        student = person("is_full_time_student", period)
        min_age = where(student, min_age_student, min_age_non_student)
        max_age = parameters.gov.irs.credits.eitc.eligibility.age.max(period)
        # IRC 32(c)(1)(A)(ii)(II): "attained age 25 but not attained age 65
        # before the close of the taxable year". The parameter is the highest
        # completed age that qualifies, so compare completed years: a filer
        # aged 64.5 has not attained 65. The minimum already works for
        # fractional ages. This reads `age` as the age at the close of the
        # taxable year.
        meets_age_requirements = (age >= min_age) & (np.floor(age) <= max_age)
        # IRC § 32(c)(1)(A)(ii)(II) applies the age test to the filer or,
        # on a joint return, either spouse — never to dependents.
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        # IRC § 32(c)(1)(A)(ii)(III): without a qualifying child, the filer
        # must not be a dependent of another taxpayer; on a joint return,
        # "neither you nor your spouse can be claimed as a dependent by another
        # person" (IRS Publication 596). A nonrequired claimant who files
        # no return or only for a withholding/estimated-payment refund is
        # excepted, without changing the standard-deduction limitation.
        dependent_elsewhere = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        childless_eligible = (
            tax_unit.any(meets_age_requirements & is_filer_or_spouse)
            & ~dependent_elsewhere
        )
        return has_child | childless_eligible
