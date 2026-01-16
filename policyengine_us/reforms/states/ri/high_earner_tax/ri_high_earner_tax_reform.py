from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_high_earner_tax() -> Reform:
    class ri_income_tax_before_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island income tax before refundable credits"
        defined_for = StateCode.RI
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            income = tax_unit("ri_taxable_income", period)
            p_baseline = parameters(period).gov.states.ri.tax.income.rate
            p_reform = parameters(period).gov.contrib.states.ri.high_earner_tax

            # If reform is in effect, use new 2027 bracket structure
            # Per §44-30-2.6(c)(3)(A): fixed thresholds of $55k, $125k, $648,398
            if p_reform.in_effect:
                # New bracket thresholds for 2027+
                bracket1_threshold = 55_000
                bracket2_threshold = 125_000
                bracket3_threshold = p_reform.threshold  # 648,398

                # Rates: 3.75%, 4.75%, 5.99%, 8.99%
                rate1 = 0.0375
                rate2 = 0.0475
                rate3 = 0.0599
                rate4 = p_reform.rate  # 0.0899

                # Calculate tax using new bracket structure
                tax_bracket1 = min_(income, bracket1_threshold) * rate1
                tax_bracket2 = (
                    max_(
                        min_(income, bracket2_threshold) - bracket1_threshold,
                        0,
                    )
                    * rate2
                )
                tax_bracket3 = (
                    max_(
                        min_(income, bracket3_threshold) - bracket2_threshold,
                        0,
                    )
                    * rate3
                )
                tax_bracket4 = max_(income - bracket3_threshold, 0) * rate4

                return (
                    tax_bracket1 + tax_bracket2 + tax_bracket3 + tax_bracket4
                )
            else:
                # Use baseline brackets
                return p_baseline.calc(income)

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_income_tax_before_non_refundable_credits)

    return reform


def create_ri_high_earner_tax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ri_high_earner_tax()

    p = parameters.gov.contrib.states.ri.high_earner_tax

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_high_earner_tax()
    else:
        return None


ri_high_earner_tax = create_ri_high_earner_tax_reform(None, None, bypass=True)
