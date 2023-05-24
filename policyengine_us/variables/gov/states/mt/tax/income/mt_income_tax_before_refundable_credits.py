from policyengine_us.model_api import *


class mt_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montanta income tax before refunable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        income = tax_unit("mt_taxable_income", period)
        p = parameters(period).gov.states.mt.tax.income.main
        # Before 2024 Montana has a flat tax rate for each filing status
        temporary_rate = p.temporary_rate.calc(income)
        # After 2024 the tax rate depends on the filing status
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        progressive_rate = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
            ],
            [
                p.progressive.single.calc(income),
                p.progressive.joint.calc(income),
                p.progressive.head_of_household.calc(income),
                p.progressive.separate.calc(income),
            ],
        )
        rate_change = period.start.year >= 2024
        return where(rate_change, progressive_rate, temporary_rate)
