from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class oh_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.054",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.oh.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "oh_income_tax_before_non_refundable_credits",
            "oh_cdcc",
            "oh_cdcc_potential",
        )
