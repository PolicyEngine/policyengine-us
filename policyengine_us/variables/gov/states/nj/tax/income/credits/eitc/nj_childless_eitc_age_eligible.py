from policyengine_us.model_api import *
from policyengine_us.tools.section_911 import elects_section_911_exclusion


class nj_childless_eitc_age_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New Jersey Eligible for EITC"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/",
        # P.L. 2021, c.130, section 1a(4): the filer "shall meet all
        # qualifications, except for the minimum or maximum age, for the
        # federal earned income tax credit".
        "https://pub.njleg.state.nj.us/Bills/2020/PL21/130_.HTM",
        "https://www.law.cornell.edu/uscode/text/26/32#c_1_A_ii",
        # 2025 NJ-1040 instructions, line 58.
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

        # Check if the filer meets NJ EITC age requirements. The age test
        # applies to the filer or, on a joint return, either spouse, never to
        # a dependent (IRC 32(c)(1)(A)(ii)(II)).
        age = person("age", period)
        is_filer_or_spouse = ~person("is_tax_unit_dependent", period)
        age_eligible = (age >= p.eligibility.age.min) & is_filer_or_spouse

        # Section 32(c)(1)(C): a filer who claims the benefits of section 911
        # fails a federal qualification other than age.
        claims_section_911 = elects_section_911_exclusion(tax_unit, period)

        # Section 32(c)(1)(A)(ii)(III): without a qualifying child, the filer
        # must not be a dependent of another taxpayer, and on a joint return
        # neither spouse may be. The NJ-1040 line 58 worksheet also requires
        # "You are not listed as a dependent on another tax return."
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)

        return (
            ~separate
            & no_qualifying_children
            & tax_unit.any(age_eligible)
            & tax_unit("nj_eitc_income_eligible", period)
            & ~claims_section_911
            & ~dependent_elsewhere
        )
