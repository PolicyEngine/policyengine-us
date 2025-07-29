from policyengine_us.model_api import *


class charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction"
    unit = USD
    documentation = "Deduction from taxable income for charitable donations."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(
            tax_unit, period, ["charitable_non_cash_donations"]
        )
        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity
        capped_non_cash_donations = min_(
            non_cash_donations, p.ceiling.non_cash * positive_agi
        )

        total_cap = p.ceiling.all * positive_agi
        if p.floor.applies:
            deduction_floor = p.floor.amount * positive_agi
            reduced_non_cash_donations = max_(
                non_cash_donations - deduction_floor, 0
            )
            capped_reduced_non_cash_donations = min_(
                reduced_non_cash_donations, p.ceiling.non_cash * positive_agi
            )

            remaining_floor = max_(deduction_floor - non_cash_donations, 0)
            reduced_cash_donations = max_(cash_donations - remaining_floor, 0)
            return min_(
                capped_reduced_non_cash_donations + reduced_cash_donations,
                total_cap,
            )
        return min_(capped_non_cash_donations + cash_donations, total_cap)
