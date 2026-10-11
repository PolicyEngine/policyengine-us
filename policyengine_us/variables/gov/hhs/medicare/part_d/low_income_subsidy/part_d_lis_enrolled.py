from policyengine_us.model_api import *


class part_d_lis_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in the Medicare Part D low-income subsidy"
    documentation = (
        "Medicare enrolls Medicaid enrollees and Supplemental Security Income "
        "recipients in a Part D plan with the subsidy without an application. "
        "Other eligible people receive it if they take it up."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(c)(2)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3101",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-B/section-423.34",
    )
    defined_for = "part_d_lis_eligible"

    def formula(person, period, parameters):
        medicaid = person("medicaid_enrolled", period)
        ssi = add(person, period, ["ssi"]) > 0
        takes_up = person("takes_up_part_d_lis_if_eligible", period)
        return medicaid | ssi | takes_up
