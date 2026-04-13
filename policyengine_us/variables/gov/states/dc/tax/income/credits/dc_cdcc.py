from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class dc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=36"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=34"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.dc.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "dc_income_tax_before_credits",
            "dc_cdcc",
            "dc_cdcc_potential",
        )
