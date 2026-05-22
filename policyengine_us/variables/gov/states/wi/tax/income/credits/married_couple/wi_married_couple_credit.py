from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class wi_married_couple_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin married couple credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4"
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=21"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4"
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=21"
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.wi.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "wi_income_tax_before_credits",
            "wi_married_couple_credit",
            "wi_married_couple_credit_potential",
        )
