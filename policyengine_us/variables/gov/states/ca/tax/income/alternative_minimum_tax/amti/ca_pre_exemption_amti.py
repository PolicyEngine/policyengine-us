from policyengine_us.model_api import *


class ca_pre_exemption_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-exemption alternative minimum taxable income"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2024/2024-540-p.pdf#page=1"

    # Schedule P (540) Part I, line 19: combine regular taxable income
    # (line 15) with the total AMT adjustments and preferences (line 14) and
    # subtract the restored itemized deductions limitation (line 18).
    #
    # ca_amti_adjustments (line 14) adds back only the specific AMT-disallowed
    # itemized deductions (property taxes, medical, etc.), so the full
    # pre-limitation itemized deductions must NOT be added on top; doing so
    # double-counts disallowed items and adds back deductions (e.g. charity,
    # acquisition mortgage interest) that AMT still allows.
    adds = [
        "ca_amti_adjustments",
        "ca_taxable_income",
    ]
    subtracts = [
        "ca_itemized_deductions_limitation",
    ]
