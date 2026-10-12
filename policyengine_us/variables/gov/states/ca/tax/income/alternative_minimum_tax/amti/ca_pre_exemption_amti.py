from policyengine_us.model_api import *


class ca_pre_exemption_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-exemption alternative minimum taxable income"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2024/2024-540-p.pdf#page=1",
        "https://www.ftb.ca.gov/forms/2025/2025-540-p-instructions.html",
    )

    # Schedule P (540) Part I, line 19: combine signed taxable income
    # (line 15) with the total AMT adjustments and preferences (line 14) and
    # subtract the restored itemized deductions limitation (line 18).
    #
    # ca_amti_adjustments (line 14) adds back only the specific AMT-disallowed
    # itemized deductions (property taxes, medical, etc.), so the full
    # pre-limitation itemized deductions must NOT be added on top; doing so
    # double-counts disallowed items and adds back deductions (e.g. charity,
    # acquisition mortgage interest) that AMT still allows.
    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ca_taxable_income", period)
        # Line 15: when Form 540 line 19 is zero, use the signed difference
        # between AGI (line 17) and deductions (line 18) before AMT add-backs.
        signed_taxable_income = where(
            taxable_income == 0,
            tax_unit("ca_agi", period) - tax_unit("ca_deductions", period),
            taxable_income,
        )
        adjustments = tax_unit("ca_amti_adjustments", period)
        limitation = tax_unit("ca_itemized_deductions_limitation", period)
        return signed_taxable_income + adjustments - limitation
