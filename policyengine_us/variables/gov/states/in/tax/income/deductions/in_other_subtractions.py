from policyengine_us.model_api import *


class in_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    documentation = (
        "Indiana other deductions reported on Form IT-40, Schedule 2, Line 11 "
        "(Other Deductions), entered as a positive amount. Excludes deduction codes "
        "PolicyEngine computes separately: 601, 602, 621, 632, and 643, and for "
        "2026 only the tip, overtime, and car loan interest deductions."
    )
    # PDF pages 19-24
    reference = "https://forms.in.gov/Download.aspx?id=16915#page=19"
