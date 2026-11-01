from policyengine_us.model_api import *


class ca_is_qualifying_child_for_caleitc(Variable):
    value_type = bool
    entity = Person
    label = "Child qualifies for CalEITC"
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/file/personal/credits/EITC-calculator/Help/QualifyingChildren",
        # RTC 17052 conforms CalEITC to the IRC 32 qualifying-child definition.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052",
        # IRC 32(c)(3)(A) applies the IRC 152(c) qualifying-child definition.
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_A",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # CalEITC uses federal EITC rules regarding qualifying children,
        # including the IRC 152(c)(3)(B) age waiver for a permanently and
        # totally disabled dependent and the IRC 152(c)(2) relationship test.
        return person("is_eitc_qualifying_child", period)
