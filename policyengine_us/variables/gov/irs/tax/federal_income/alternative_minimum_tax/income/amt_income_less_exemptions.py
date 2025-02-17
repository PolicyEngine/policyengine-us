from policyengine_us.model_api import *


class amt_income_less_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax Income less exemptions"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) income less exemptions"

    def formula(tax_unit, period, parameters):
        # Form 6251, Part I
        # Line 4
        amt_income = tax_unit("amt_income", period)
        # For filers subject to the kiddie tax, the deductions are not added back
        taxable_income = tax_unit("taxable_income", period)
        kiddie_tax_applies = tax_unit("amt_kiddie_tax_applies", period)
        applied_income = where(kiddie_tax_applies, taxable_income, amt_income)
        # Form 6251, Part II top
        p = parameters(period).gov.irs.income.amt
        phase_out = p.exemption.phase_out
        filing_status = tax_unit("filing_status", period)
        # Line 5 the exemption amount is based on filing status and
        # is phased-out at higher income
        base_exemption_amount = p.exemption.amount[filing_status]
        income_excess = max_(0, amt_income - phase_out.start[filing_status])
        exemption_phase_out = phase_out.rate * income_excess
        reduced_exemption_amount = max_(
            0,
            (base_exemption_amount - exemption_phase_out),
        )
        # A reduced exemption amount is applied to kiddie tax filers
        adj_earnings = tax_unit("filer_adjusted_earnings", period)
        child_amount = p.exemption.child.amount

        exemption_cap = where(
            kiddie_tax_applies,
            adj_earnings + child_amount,
            np.inf,
        )
        capped_exemption_amount = min_(reduced_exemption_amount, exemption_cap)
        # Line 6
        return max_(0, applied_income - capped_exemption_amount)
