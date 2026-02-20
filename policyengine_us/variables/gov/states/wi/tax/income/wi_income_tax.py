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
        refundable = tax_unit("wi_refundable_credits", period)
        standard_tax = before_refundable - refundable
        p = parameters(
            period
        ).gov.states.wi.tax.income.subtractions.retirement_income.exclusion
        if p.in_effect:
            exclusion_tax = tax_unit(
                "wi_retirement_income_exclusion_tax", period
            )
            return min_(standard_tax, exclusion_tax)
        return standard_tax
