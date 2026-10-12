from policyengine_us.model_api import *


class ca_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf",
        # 2020 Schedule CA (540) instructions, Part I, Section C, line 22,
        # column B: the federal Form 1040 line 10b charitable deduction.
        "https://www.ftb.ca.gov/forms/2020/2020-540-booklet.pdf#page=48",
    )
    defined_for = StateCode.CA
    adds = [
        "ca_hsa_addition",
        "ca_educator_expense_addition",
        "charitable_contributions_ald",
    ]
