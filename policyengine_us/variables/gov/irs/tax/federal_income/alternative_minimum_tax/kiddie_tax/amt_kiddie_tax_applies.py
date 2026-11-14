from policyengine_us.model_api import *


class amt_kiddie_tax_applies(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax kiddie tax applies"
    documentation = (
        "Whether IRC 1(g) applies to the filer, for the IRC 59(j) AMT child "
        "exemption limitation, which IRC 55(d)(4)(A)(iii) turns off for "
        "taxable years beginning after 2017. The filer must be under 18, or "
        "meet the IRC 152(c)(3) age test with earned income no more than "
        "half of their support (care_and_support_costs; the model treats the "
        "support test as met when nobody reports support), and must not file "
        "a joint return. The model has no input for whether a parent is alive "
        "at year end (IRC 1(g)(2)(B)), so it assumes one is."
    )
    reference = [
        "https://www.govinfo.gov/content/pkg/USCODE-2016-title26/html/USCODE-2016-title26-subtitleA-chap1-subchapA-partI-sec1.htm",
        "https://www.law.cornell.edu/uscode/text/26/1#g_2",
        "https://www.irs.gov/pub/irs-prior/i6251--2017.pdf#page=10",
        "https://www.irs.gov/pub/irs-prior/p929--2021.pdf",
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs
        age_limit = p.dependent.ineligible_age
        support_test = p.income.amt.exemption.child.support_test

        # IRC 1(g)(2) looks at the filer alone, so only the head's facts
        # count. A spouse matters only through the joint-return exclusion.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        head_is_student = tax_unit.any(person("is_full_time_student", period) & is_head)
        age_head = tax_unit("age_head", period)
        # IRC 1(g)(2)(A)(i): under 18 at the close of the year.
        under_support_test_age = (age_head != 0) & (
            age_head < support_test.age_threshold
        )
        # IRC 1(g)(2)(A)(ii)(I): otherwise, the IRC 152(c)(3) age test
        # (under 19, or under 24 if a full-time student).
        meets_dependent_age_test = (age_head != 0) & (
            age_head < where(head_is_student, age_limit.student, age_limit.non_student)
        )
        # IRC 1(g)(2)(A)(ii)(II): earned income (IRC 911(d)(2)) no more than
        # half of the child's support. Every living person has some support,
        # so zero means nobody reported it, and the model treats the test as
        # met.
        earned_income = tax_unit.sum(person("adjusted_earnings", period) * is_head)
        support = tax_unit.sum(person("care_and_support_costs", period) * is_head)
        support_reported = support > 0
        meets_support_test = ~support_reported | (
            earned_income <= support_test.rate * support
        )
        meets_age_test = under_support_test_age | (
            meets_dependent_age_test & meets_support_test
        )

        # The model assumes a living parent (IRC 1(g)(2)(B)), because no input
        # links the filer to a parent. IRC 1(g)(2)(C) excludes joint returns.
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        return meets_age_test & ~joint
