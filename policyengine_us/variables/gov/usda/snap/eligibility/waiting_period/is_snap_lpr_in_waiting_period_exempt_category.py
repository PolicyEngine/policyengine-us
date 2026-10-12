from policyengine_us.model_api import *


class is_snap_lpr_in_waiting_period_exempt_category(Variable):
    value_type = bool
    entity = Person
    label = "Lawful permanent resident admitted in or adjusted from a category exempt from the SNAP waiting period"
    documentation = (
        "Whether a lawful permanent resident was admitted for permanent "
        "residence in, or adjusted to that status from, a category exempt "
        "from the SNAP qualified alien waiting period, and so keeps the "
        "exemption (7 CFR 273.4(a)(6)(ii)(B)-(F) and (iv): each category of "
        "eligible alien status stands alone). Exempt categories include "
        "refugee, asylee, deportation or removal withheld, Cuban and Haitian "
        "entrant, Amerasian immigrant, citizen of a Compact of Free "
        "Association state, American Indian born abroad or member of a "
        "federally recognized tribe, Hmong or Highland Laotian tribal member, "
        "Iraqi or Afghan special immigrant, Afghan national paroled between "
        "July 31, 2021, and September 30, 2023, Ukrainian national paroled "
        "between February 24, 2022, and September 30, 2024, and victim of "
        "severe trafficking (the groups the FNS Question and Answer #1 "
        "REVISED, Question 5 chart marks as not subject to the waiting "
        "period). Set it also for groups admitted directly as lawful "
        "permanent residents rather than by adjustment, such as Amerasian "
        "immigrants, Iraqi and Afghan special immigrants, and American "
        "Indians born in Canada. This is how lawful permanent residents in "
        "the American Indian (8 USC 1612(a)(2)(G)) and Hmong or Highland "
        "Laotian (8 USC 1612(a)(2)(K)) groups are exempted. ImmigrationStatus "
        "records only current status, so this input carries the category. "
        "The list follows SNAP; other programs, such as Medicaid, exempt a "
        "different set of groups from their five-year bars. Defaults to "
        "false. The SNAP waiting period reads it only for lawful permanent "
        "residents."
    )
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.law.cornell.edu/uscode/text/8/1613#b_1",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6_iv",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility.pdf#page=2",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=3",
        "https://www.usda.gov/sites/default/files/guidance-documents/fns.snap-obbb-alien-eligibility-qas1.pdf#page=4",
    )
