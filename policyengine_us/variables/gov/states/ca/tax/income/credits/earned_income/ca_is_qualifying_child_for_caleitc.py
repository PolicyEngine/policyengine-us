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
        # IRC 152(c)(3)(B) waives the qualifying-child age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        # CalEITC uses federal EITC rules regarding qualifying children.
        # IRC 152(c)(3)(B) waives the age test for a permanently and totally
        # disabled dependent, so such a dependent qualifies at any age.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        return person("is_qualifying_child_dependent", period) | is_disabled_dependent
