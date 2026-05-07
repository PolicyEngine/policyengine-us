from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class ct_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2021/Income/CT-1040-Online-Booklet_1221.pdf#page=30"
    defined_for = "ct_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.ct.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "ct_income_tax_after_amt",
            "ct_property_tax_credit",
            "ct_property_tax_credit_potential",
        )
