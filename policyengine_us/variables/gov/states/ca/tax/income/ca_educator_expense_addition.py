from policyengine_us.model_api import *


class ca_educator_expense_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "California educator expense addition"
    documentation = (
        "Federal above-the-line educator expense deduction claimed on this "
        "return, restored to California AGI under R&TC 17072(b)."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17072",
        # Schedule CA (540), Section C, line 11.
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=64",
    )
    adds = ["educator_expense_ald"]
