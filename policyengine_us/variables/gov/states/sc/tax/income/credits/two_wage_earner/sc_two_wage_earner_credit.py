from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class sc_two_wage_earner_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina two wage earner credit"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/SC1040TT_2021.pdf",
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.sc.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "sc_income_tax_before_non_refundable_credits",
            "sc_two_wage_earner_credit",
            "sc_two_wage_earner_credit_potential",
        )
