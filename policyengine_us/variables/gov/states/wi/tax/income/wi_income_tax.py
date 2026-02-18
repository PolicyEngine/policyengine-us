from policyengine_us.model_api import *


class wi_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin income tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=3",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1-Inst.pdf#page=31",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        before_refundable = tax_unit(
            "wi_income_tax_before_refundable_credits", period
        )
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        reduction = where(
            p.in_effect,
            tax_unit("wi_retirement_income_exclusion_tax_reduction", period),
            0,
        )
        after_exclusion = max_(0, before_refundable - reduction)
        refundable = tax_unit("wi_refundable_credits", period)
        return after_exclusion - refundable
