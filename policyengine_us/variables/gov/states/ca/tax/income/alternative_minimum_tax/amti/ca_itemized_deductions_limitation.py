from policyengine_us.model_api import *


class ca_itemized_deductions_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California itemized deductions limitation restored for AMT"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2024/2024-540-p.pdf#page=1",
        "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        # Schedule P (540) Part I, line 18. For regular tax, high-AGI filers
        # have their itemized deductions reduced (California itemized
        # deductions limitation). This limitation does not apply for AMT, so
        # the amount of deductions disallowed for regular tax is restored
        # (subtracted from AMTI, since it was excluded from regular taxable
        # income on Form 540 line 19 / Schedule P line 15).
        pre_limitation = tax_unit("ca_itemized_deductions_pre_limitation", period)
        post_limitation = tax_unit("ca_itemized_deductions", period)
        itemizes = tax_unit("ca_itemizes", period)
        return where(itemizes, max_(pre_limitation - post_limitation, 0), 0)
