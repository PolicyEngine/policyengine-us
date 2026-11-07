from policyengine_us.model_api import *


class part_d_lis_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in the Medicare Part D low-income subsidy"
    documentation = (
        "Medicare pays the subsidy only for people enrolled in a Part D plan "
        "(medicare_part_d_enrolled). It enrolls Medicaid enrollees and "
        "Supplemental Security Income recipients in a plan with the subsidy "
        "without an application, unless they opt out of Part D. Other "
        "eligible people in a Part D plan receive it if they take it up."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_A",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(c)(2)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3101",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-B/section-423.34",
    )
    defined_for = "part_d_lis_eligible"

    def formula(person, period, parameters):
        in_part_d = person("medicare_part_d_enrolled", period)
        medicaid = person("medicaid_enrolled", period)
        ssi = add(person, period, ["ssi"]) > 0
        takes_up = person("takes_up_part_d_lis_if_eligible", period)
        return in_part_d & (medicaid | ssi | takes_up)
