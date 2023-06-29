from policyengine_us.model_api import *


class ma_limited_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Limited Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-schedule-nts-l-nrpy-no-tax-status-and-limited-income-credit/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ma_agi", period)
        exemption_threshold = tax_unit(
            "ma_income_tax_exemption_threshold", period
        )
        income_over_threshold = max_(0, agi - exemption_threshold)
        # Compute AGI as a share of the exemption threshold.
        # Use a mask rather than where to avoid a divide-by-zero warning. Default to inf.
        income_ratio = np.ones_like(agi) * np.inf
        mask = exemption_threshold > 0
        income_ratio[mask] = agi[mask] / exemption_threshold[mask]
        p = parameters(period).gov.states.ma.tax.income.credits
        eligible = income_ratio <= p.limited_income_credit.income_limit
        tax_cap = p.limited_income_credit.percent * income_over_threshold
        income_tax = tax_unit("ma_income_tax_before_credits", period)
        excess_tax = max_(0, income_tax - tax_cap)
        return eligible * excess_tax
