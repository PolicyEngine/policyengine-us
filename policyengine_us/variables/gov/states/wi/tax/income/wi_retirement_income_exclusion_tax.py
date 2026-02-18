from policyengine_us.model_api import *


class wi_retirement_income_exclusion_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion path tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Schedule SB Line 16 path: tax on income reduced by the
        # exclusion amount, with zero credits applied.
        line16 = tax_unit("wi_retirement_income_exclusion_amount", period)
        line17 = tax_unit("wi_retirement_income_subtraction", period)
        taxinc = tax_unit("wi_taxable_income", period)
        # Add Line 17 back because wi_taxable_income already
        # subtracted it.
        exclusion_taxinc = max_(0, taxinc - line16 + line17)

        fstatus = tax_unit("filing_status", period)
        statuses = fstatus.possible_values
        p = parameters(period).gov.states.wi.tax.income
        return select(
            [
                fstatus == statuses.SINGLE,
                fstatus == statuses.JOINT,
                fstatus == statuses.SURVIVING_SPOUSE,
                fstatus == statuses.SEPARATE,
                fstatus == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rates.single.calc(exclusion_taxinc),
                p.rates.joint.calc(exclusion_taxinc),
                p.rates.joint.calc(exclusion_taxinc),
                p.rates.separate.calc(exclusion_taxinc),
                p.rates.head_of_household.calc(exclusion_taxinc),
            ],
        )
