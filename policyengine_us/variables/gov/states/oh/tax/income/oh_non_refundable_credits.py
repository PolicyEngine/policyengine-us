from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


class oh_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio non-refundable credits"
    reference = (
        # 2021 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/sch-cre.pdf",
        # 2022 Ohio Schedule of Credits
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/itschedule-credits.pdf",
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.oh.tax.income.credits.non_refundable
        return ordered_capped_state_non_refundable_credits(
            tax_unit,
            period,
            ordered_credits,
            "oh_income_tax_before_non_refundable_credits",
        )
