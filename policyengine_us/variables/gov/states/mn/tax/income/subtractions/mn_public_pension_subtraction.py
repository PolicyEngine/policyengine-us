from policyengine_us.model_api import *


class mn_public_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota public pension subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        taxable_public_pension_income = add(
            tax_unit, period, ["taxable_public_pension_income"]
        )
        p = parameters(
            period
        ).gov.states.mn.tax.income.subtractions.pension_income
        filing_status = tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        capped_pension_income = min_(taxable_public_pension_income, cap)
        agi = tax_unit("adjusted_gross_income", period)
        agi_threshold = p.reduction.start[filing_status]
        excess = max_(0, agi - agi_threshold)
        reduced_agi_fraction = np.ceil(excess / p.reduction.increment)
        percentage = min_(p.reduction.rate * reduced_agi_fraction, 1)
        reduction = capped_pension_income * percentage
        return max_(capped_pension_income - reduction, 0)
