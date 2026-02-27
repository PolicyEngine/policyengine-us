from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_sc_h4216() -> Reform:
    """
    South Carolina H.4216 - Comprehensive Income Tax Reform

    This bill makes several changes to SC income tax:
    1. Caps the SC EITC at $200 (Section 7)
    2. Creates the SC Income Adjusted Deduction (SCIAD) replacing federal
       standard deduction (Section 3)
    3. Establishes new tax rates: 1.99% up to $30k, 5.21% above (Section 1)

    Reference: https://www.scstatehouse.gov/sess126_2025-2026/prever/4216_20260224.htm
    """

    class sc_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina EITC under H.4216"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.scstatehouse.gov/sess126_2025-2026/prever/4216_20260224.htm",
            "https://dor.sc.gov/forms-site/Forms/TC60_2021.pdf",
        )
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            federal_eitc = tax_unit("eitc", period)
            p = parameters(period).gov.states.sc.tax.income.credits.eitc
            p_h4216 = parameters(period).gov.contrib.states.sc.h4216.eitc
            # Calculate 125% of federal EITC, then cap at $200
            uncapped = np.round(federal_eitc * p.rate, 1)
            return min_(uncapped, p_h4216.max)

    class sc_sciad(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina Income Adjusted Deduction (SCIAD)"
        unit = USD
        definition_period = YEAR
        reference = "https://www.scstatehouse.gov/sess126_2025-2026/prever/4216_20260224.htm"
        defined_for = StateCode.SC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.sc.h4216.sciad
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)

            # Get base amount and phase-out parameters by filing status
            base_amount = p.amount[filing_status]
            phase_out_start = p.phase_out.start[filing_status]
            phase_out_width = p.phase_out.width[filing_status]

            # Calculate phase-out reduction
            # Formula: deduction * (1 - (AGI - phase_out_start) / width)
            excess_agi = max_(agi - phase_out_start, 0)
            phase_out_fraction = min_(excess_agi / phase_out_width, 1)
            raw_sciad = max_(base_amount * (1 - phase_out_fraction), 0)
            # Per H.4216 Section 3, round down to nearest $10
            return np.floor(raw_sciad / 10) * 10

    class sc_taxable_income(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina taxable income under H.4216"
        defined_for = StateCode.SC
        unit = USD
        definition_period = YEAR
        reference = "https://www.scstatehouse.gov/sess126_2025-2026/prever/4216_20260224.htm"

        def formula(tax_unit, period, parameters):
            # Start with federal AGI (H.4216 replaces federal std/itemized
            # with SCIAD). Baseline sc_additions (QBI addback, SALT addback)
            # exist to undo federal deductions already embedded in federal
            # taxable_income; since we start from AGI those deductions were
            # never taken, so additions must be excluded.
            agi = tax_unit("adjusted_gross_income", period)
            subtractions = tax_unit("sc_subtractions", period)
            sciad = tax_unit("sc_sciad", period)
            return max_(0, agi - subtractions - sciad)

    class sc_income_tax_before_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "South Carolina income tax before non-refundable credits under H.4216"
        defined_for = StateCode.SC
        unit = USD
        definition_period = YEAR
        reference = "https://www.scstatehouse.gov/sess126_2025-2026/prever/4216_20260224.htm"

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("sc_taxable_income", period)
            # Use H.4216 rates instead of baseline rates
            p = parameters(period).gov.contrib.states.sc.h4216.rates
            return p.calc(taxable_income)

    class reform(Reform):
        def apply(self):
            self.update_variable(sc_eitc)
            self.update_variable(sc_sciad)
            self.update_variable(sc_taxable_income)
            self.update_variable(sc_income_tax_before_non_refundable_credits)

    return reform


def create_sc_h4216_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_sc_h4216()

    p = parameters.gov.contrib.states.sc.h4216

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_sc_h4216()
    else:
        return None


sc_h4216 = create_sc_h4216_reform(None, None, bypass=True)
