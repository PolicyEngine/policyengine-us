from policyengine_us.model_api import *


class agi_plus_section_911_931_933_exclusions(Variable):
    value_type = float
    entity = TaxUnit
    label = "AGI plus income excluded under sections 911, 931 and 933"
    unit = USD
    documentation = (
        "Adjusted gross income increased by any amount excluded from gross "
        "income under 26 U.S.C. 911 (foreign earned income and housing), "
        "931 (income from Guam, American Samoa or the Northern Mariana "
        "Islands) or 933 (income from Puerto Rico). This is the modified "
        "adjusted gross income of the child tax credit, the education "
        "credits, the saver's credit, the clean vehicle credits, the SALT "
        "cap phase-down and the senior, tip, overtime and car loan interest "
        "deductions. Income inputs are net of the section 911 exclusion, so "
        "it is added back; sections 931 and 933 are above-the-line "
        "deductions in this model, so adding them back reverses them."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#b_1",
        "https://www.law.cornell.edu/uscode/text/26/25A#d_2",
        "https://www.law.cornell.edu/uscode/text/26/25B#e",
        "https://www.law.cornell.edu/uscode/text/26/25E#b_3",
        "https://www.law.cornell.edu/uscode/text/26/30D#f_10_C",
        "https://www.law.cornell.edu/uscode/text/26/151#d_5_C",
        "https://www.law.cornell.edu/uscode/text/26/163#h_4_C",
        "https://www.law.cornell.edu/uscode/text/26/164#b_7_B",
        "https://www.law.cornell.edu/uscode/text/26/224#b_2_B",
        "https://www.law.cornell.edu/uscode/text/26/225#b_2_B",
    )
    adds = [
        "adjusted_gross_income",
        "foreign_earned_income_exclusion",
        "specified_possession_income",
        "puerto_rico_income",
    ]
