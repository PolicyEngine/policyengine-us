from policyengine_us.model_api import *


class ca_out_of_state_municipal_bond_interest(Variable):
    value_type = float
    entity = Person
    label = "Municipal bond interest taxable in California from other states"
    unit = USD
    definition_period = YEAR
    default_value = 0
    min_value = 0
    documentation = (
        "Nonnegative portion of tax_exempt_interest_income from state or local "
        "bonds issued outside California, added to California AGI on Schedule "
        "CA (540), Part I, Section A, line 2, column C under R&TC 17143. "
        "Include this amount in tax_exempt_interest_income too: it is a subset "
        "of that total, not additional income, and does not increase federal "
        "AGI. Only nondependent members' amounts enter their tax unit's AGI; "
        "a dependent's interest belongs on their own return, and a parent "
        "election to report it is not inferred. The default is zero, so "
        "absent issuer-source data all tax-exempt "
        "interest is treated as California-source for this adjustment. "
        "California state and local bond interest remains exempt under "
        "R&TC 17133."
    )
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17143",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17133",
        "https://www.ftb.ca.gov/forms/2023/2023-1001-publication.pdf#page=7",
        "https://www.ftb.ca.gov/forms/2025/2025-1001-publication.pdf#page=8",
        "https://www.ftb.ca.gov/forms/2025/2025-3803-instructions.html",
    )
