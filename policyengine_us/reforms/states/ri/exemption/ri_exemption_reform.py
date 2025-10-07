from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_exemption_reform() -> Reform:
    class ri_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            # Check if reform is in effect
            p_reform = parameters(
                period
            ).gov.contrib.states.ri.dependent_exemption
            p_base = parameters(period).gov.states.ri.tax.income.exemption

            if p_reform.in_effect:
                # Personal exemptions use baseline amount
                filing_status = tax_unit("filing_status", period)
                personal_exemptions = where(
                    filing_status == filing_status.possible_values.JOINT,
                    2,
                    1,
                )
                personal_exemption_amount = personal_exemptions * p_base.amount

                # Determine eligible dependents
                person = tax_unit.members
                age = person("age", period)
                is_dependent = person("is_tax_unit_dependent", period)

                # Apply age limit if in effect
                if p_reform.age_limit.in_effect:
                    age_threshold = p_reform.age_limit.threshold
                    eligible_dependents = is_dependent & (age < age_threshold)
                else:
                    eligible_dependents = is_dependent

                dependents_count = tax_unit.sum(eligible_dependents)
                dependent_exemption_amount = dependents_count * p_reform.amount

                # Total exemption before phaseout
                total_exemption = (
                    personal_exemption_amount + dependent_exemption_amount
                )

                # Apply phaseout to dependent exemptions only
                phaseout = 0

                # AGI-based phaseout
                if p_reform.phaseout.agi_based.in_effect:
                    mod_agi = tax_unit("ri_agi", period)
                    threshold = p_reform.phaseout.agi_based.threshold[
                        filing_status
                    ]
                    excess_agi = max_(0, mod_agi - threshold)
                    phaseout = excess_agi * p_reform.phaseout.agi_based.rate

                # Earnings-based phaseout
                elif p_reform.phaseout.earnings_based.in_effect:
                    earnings = tax_unit("tax_unit_earned_income", period)
                    threshold = p_reform.phaseout.earnings_based.threshold[
                        filing_status
                    ]
                    excess_earnings = max_(0, earnings - threshold)
                    phaseout = (
                        excess_earnings * p_reform.phaseout.earnings_based.rate
                    )

                # Apply phaseout only to dependent exemptions
                reduced_dependent_exemption = max_(
                    dependent_exemption_amount - phaseout, 0
                )

                return personal_exemption_amount + reduced_dependent_exemption
            else:
                # Use baseline exemption calculation
                p = p_base
                exemptions_count = tax_unit("exemptions_count", period)
                exemption_amount = exemptions_count * p.amount

                # Modified Federal AGI
                mod_agi = tax_unit("ri_agi", period)

                excess_agi = max_(0, mod_agi - p.reduction.start)
                increments = np.ceil(excess_agi / p.reduction.increment)
                reduction_rate = min_(p.reduction.rate * increments, 1)

                return exemption_amount * (1 - reduction_rate)

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_exemptions)

    return reform


def create_ri_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ri_exemption_reform()

    p = parameters.gov.contrib.states.ri.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_exemption_reform()
    else:
        return None


ri_exemption_reform = create_ri_exemption_reform_fn(None, None, bypass=True)
