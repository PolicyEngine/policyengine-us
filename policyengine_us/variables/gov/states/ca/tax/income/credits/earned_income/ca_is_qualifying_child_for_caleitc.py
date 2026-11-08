from policyengine_us.model_api import *


class ca_is_qualifying_child_for_caleitc(Variable):
    value_type = bool
    entity = Person
    label = "Child qualifies for CalEITC"
    documentation = """
    An IRC 32(c)(3) qualifying child who meets California's identification
    requirement. Before 2020 that is the federal rule (an SSN valid for
    work); from 2020, R&TC 17052(p) accepts an SSN of any kind or an ITIN.
    CalEITC counts these children, and the young child tax credit
    (R&TC 17052.1) requires one under age 6.
    """
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/file/personal/credits/EITC-calculator/Help/QualifyingChildren",
        # RTC 17052 conforms CalEITC to the IRC 32 qualifying-child definition;
        # 17052(p) modifies the IRC 32(m) identification rule from 2020.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.",
        # RTC 17052.1(c): "'Qualifying child' shall have the same meaning as
        # under Section 17052, except that the child shall be younger than six
        # years of age as of the last day of the taxable year."
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.1.",
        # IRC 32(c)(3)(A) applies the IRC 152(c) qualifying-child definition.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_A",
        # FTB 3514, Line 7: a child without an SSN or ITIN cannot count for
        # the EITC or YCTC.
        "https://www.ftb.ca.gov/forms/2024/2024-3514-booklet.html",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # CalEITC uses federal EITC rules regarding qualifying children,
        # including the IRC 152(c)(3)(B) age waiver for a permanently and
        # totally disabled dependent and the IRC 152(c)(2) relationship test.
        is_child = person("is_eitc_qualifying_child", period)
        p = parameters(period).gov.states.ca.tax.income.credits.earned_income
        if p.eligibility.itin_eligible:
            # R&TC 17052(p) substitutes "federal individual taxpayer
            # identification number or a social security number" for "social
            # security number" in IRC 32(m), and drops the benefits-only SSN
            # exclusion.
            meets_identification = person("has_tin", period)
        else:
            meets_identification = person(
                "meets_eitc_identification_requirements", period
            )
        return is_child & meets_identification
