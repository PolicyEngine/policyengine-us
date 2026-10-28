from policyengine_us.model_api import *


class me_childless_eitc_age_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "In the Maine childless EITC age expansion cohort"
    documentation = (
        "A filer without a qualifying child whom 36 M.R.S. § 5219-S(6) adds to "
        "the eligible individuals: the filer or, on a joint return, either "
        "spouse is 18 to 24, and neither meets the federal EITC age test."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.maine.gov/statutes/36/title36sec5219-S.html",
        # 2021: the federal minimum age is 19, or 24 for a specified student,
        # and there is no maximum.
        "https://www.law.cornell.edu/uscode/text/26/32#n",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # 36 M.R.S. Sec. 5219-S(6) extends "eligible individual" to a filer
        # without a qualifying child who is at least 18 and has not attained 25
        # before the close of the tax year. A filer in that range who meets the
        # federal age test is already eligible under Sec. 32(c)(1) and needs no
        # expansion. This variable flags the rest: the added cohort, whose
        # credit Sec. 5219-S(5) computes as if they were federally eligible.
        p = parameters(period).gov.states.me.tax.income.credits.eitc

        person = tax_unit.members
        no_qualifying_children = tax_unit("eitc_child_count", period) == 0

        age = person("age", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        in_maine_age_range = (
            (age >= p.eligibility.age.min)
            & (age <= p.eligibility.age.max)
            & is_head_or_spouse
        )

        # The federal age test of IRC Sec. 32(c)(1)(A)(ii)(II), read as in
        # eitc_demographic_eligible. In 2021 the minimum age was 19, or 24 for
        # a student, with no maximum (Sec. 32(n)(1)-(2)), so a student aged 19
        # to 23 fails it even though a non-student of the same age passes.
        federal_age = parameters.gov.irs.credits.eitc.eligibility.age
        student = person("is_full_time_student", period)
        federal_min_age = where(
            student, federal_age.min_student(period), federal_age.min(period)
        )
        meets_federal_age = (
            (age >= federal_min_age)
            & (age <= federal_age.max(period))
            & is_head_or_spouse
        )

        return (
            no_qualifying_children
            & tax_unit.any(in_maine_age_range)
            & ~tax_unit.any(meets_federal_age)
        )
