from policyengine_us.model_api import *


class part_d_lis_enrolled(Variable):
    value_type = bool
    entity = Person
    label = "Enrolled in the Medicare Part D low-income subsidy"
    documentation = (
        "Medicare pays the subsidy only for people enrolled in a Part D plan "
        "(medicare_part_d_enrolled). Medicaid enrollees and Supplemental "
        "Security Income recipients get the subsidy without applying; other "
        "eligible people in a plan get it if they take it up. CMS enrolls "
        "subsidy-eligible people who don't choose a plan, and any of them "
        "can decline (42 CFR 423.34(d)(1) and (e)). Qualifying covered "
        "retirees, whose employer retiree drug coverage qualifies for the "
        "retiree drug subsidy, are the exception: CMS enrolls only the "
        "full-benefit dual eligibles among them whose plan sponsor it "
        "approved for that subsidy, and only if they confirm that they want "
        "a plan (423.34(d)(3)). So microdata that set "
        "takes_up_medicare_part_d_if_eligible should set it true for "
        "Medicaid enrollees and SSI recipients other than those who decline "
        "and covered retirees who don't choose a plan; a person whose Part D "
        "input is false gets no subsidy. "
        "Not modeled: people deemed eligible from July to December stay "
        "deemed eligible through the following year (423.773(c)(2)(ii)); the "
        "model tests each year on its own."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_A",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(c)(2)",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3101",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-B/section-423.34#p-423.34(d)",
    )
    defined_for = "part_d_lis_eligible"

    def formula(person, period, parameters):
        in_part_d = person("medicare_part_d_enrolled", period)
        medicaid = person("medicaid_enrolled", period)
        ssi = add(person, period, ["ssi"]) > 0
        takes_up = person("takes_up_part_d_lis_if_eligible", period)
        return in_part_d & (medicaid | ssi | takes_up)
