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
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Return True if all federal EITC conditions are met, except with modified age paramaters and household has no children.
        # P.L.2021, c.130 waives only the federal minimum and maximum ages,
        # so the unit must still meet the federal marital condition in
        # IRC 32(d), and New Jersey's own bar on married separate filers in
        # section 1a.(3).
        marital_eligible = tax_unit("eitc_marital_eligible", period)
        nj_separate_filer_eligible = tax_unit("nj_eitc_separate_filer_eligible", period)
        # Check if tax unit has any EITC qualifying children.
        person = tax_unit.members
        no_qualifying_children = tax_unit("eitc_child_count", period) == 0

        # Get the NJ EITC paramaeter tree.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc

        # Check if the filer meets NJ EITC age requirements.
        age = person("age", period)
        age_eligible = age >= p.eligibility.age.min

        # Section 32(c)(1)(C): a filer who claims the benefits of section 911
        # fails a federal qualification other than age.
        claims_section_911 = elects_section_911_exclusion(tax_unit, period)

        return (
            marital_eligible
            & nj_separate_filer_eligible
            & no_qualifying_children
            & tax_unit.any(age_eligible)
            & tax_unit("nj_eitc_income_eligible", period)
            & ~claims_section_911
        )
