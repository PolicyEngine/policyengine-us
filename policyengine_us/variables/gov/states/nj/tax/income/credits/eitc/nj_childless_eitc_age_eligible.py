from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import elects_section_911_exclusion


class nj_childless_eitc_age_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Eligible for EITC"
    documentation = (
        "Eligible for the New Jersey EITC as a filer without a qualifying child "
        "who is at least 18, fails the federal age requirements, and meets the "
        "federal identification, investment income, adjusted gross income and "
        "section 911 requirements. nj_eitc also requires a positive federal "
        "credit recomputed without the age test."
    )
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/",
        # P.L. 2021, c.130, section 1a(4): the filer "is ineligible to claim
        # the federal earned income tax credit due to age requirements" and
        # "shall meet all qualifications, except for the minimum or maximum
        # age, for the federal earned income tax credit".
        "https://pub.njleg.state.nj.us/Bills/2020/PL21/130_.HTM",
        # 2025 NJ-1040 instructions, line 58: "You met all federal EIC
        # requirements except the age requirement".
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=44",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Return True if all federal EITC conditions are met, except with modified age paramaters and household has no children.
        # Check if filing status is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Check if tax unit has any EITC qualifying children.
        person = tax_unit.members
        no_qualifying_children = tax_unit("eitc_child_count", period) == 0

        # Get the NJ EITC paramaeter tree.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc

        # The age tests apply to the filer or, on a joint return, either
        # spouse, never to a dependent (IRC 32(c)(1)(A)(ii)(II)).
        age = person("age", period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)

        # Check if the filer meets NJ EITC age requirements.
        age_eligible = (age >= p.eligibility.age.min) & is_filer_or_spouse

        # Section 1a(4) reaches only a filer who "is ineligible to claim the
        # federal earned income tax credit due to age requirements": no filer
        # or spouse meets the federal minimum and maximum ages, as tested in
        # eitc_demographic_eligible. A childless filer who meets them gets 40%
        # of the federal credit, not the age-path amount.
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        federal_age = parameters.gov.irs.credits.eitc.eligibility.age
        student = person("is_full_time_student", period)
        federal_min_age = where(
            student, federal_age.min_student(period), federal_age.min(period)
        )
        meets_federal_age = (age >= federal_min_age) & (age <= federal_age.max(period))
        federal_age_ineligible = ~tax_unit.any(meets_federal_age & is_filer_or_spouse)

        # IRC 32(c)(1)(E) and 32(m): the filer and any spouse need a social
        # security number valid for the EITC. New Jersey waives only the age
        # requirements.
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)

        # Section 32(c)(1)(C): a filer who claims the benefits of section 911
        # fails a federal qualification other than age.
        claims_section_911 = elects_section_911_exclusion(tax_unit, period)

        # Not yet applied here: the bar on a filer who is a dependent of
        # another taxpayer (IRC 32(c)(1)(A)(ii)(III)), which NJ-1040 line 58
        # repeats ("You are not listed as a dependent on another tax return").
        return (
            ~separate
            & no_qualifying_children
            & tax_unit.any(age_eligible)
            & federal_age_ineligible
            & filer_has_ssn
            & tax_unit("nj_eitc_income_eligible", period)
            & ~claims_section_911
        )
