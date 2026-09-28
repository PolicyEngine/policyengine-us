from policyengine_us.model_api import *


class lpr_adjusted_from_bar_exempt_status(Variable):
    value_type = bool
    entity = Person
    label = "Adjusted to lawful permanent residence from a status exempt from the five-year bar"
    documentation = (
        "Whether a lawful permanent resident adjusted to that status from a "
        "status exempt from the five-year waiting period, and so keeps the "
        "exemption (7 CFR 273.4(a)(6)(iv): each category of eligible alien "
        "status stands alone). Exempt prior statuses include refugee, asylee, "
        "deportation or removal withheld, Cuban and Haitian entrant, "
        "Amerasian, citizen of a Compact of Free Association state, American "
        "Indian born abroad, Hmong or Highland Laotian tribal member, Iraqi "
        "or Afghan special immigrant, Afghan national paroled between July "
        "31, 2021, and September 30, 2023, Ukrainian national paroled between "
        "February 24, 2022, and September 30, 2024, and victim of severe "
        "trafficking (the groups the FNS Question and Answer #1 REVISED, "
        "Question 5 chart marks as not subject to the waiting period). "
        "ImmigrationStatus records only current status, so this input carries "
        "the prior status. Defaults to false. The SNAP waiting period reads "
        "it only for lawful permanent residents."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_iv",
        "https://www.law.cornell.edu/uscode/text/8/1612#a_2_A",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=3",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=4",
    )
