from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_individual_eitc() -> Reform:
    """Individual-income EITC reform (Winship proposal).

    Computes EITC separately for each spouse based on their individual
    earnings, then sums the results. This differs from baseline EITC
    which uses combined household earnings.

    Reference: https://ifstudies.org/blog/reforming-the-eitc-to-reduce-single-parenthood-and-ease-work-family-balance
    """

    class eitc(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Federal earned income credit"
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD
        defined_for = "eitc_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.individual_eitc
            takes_up_eitc = tax_unit("takes_up_eitc", period)

            # Compute EITC separately for head and spouse
            person = tax_unit.members
            adj_earnings = person("adjusted_earnings", period)
            is_head = person("is_tax_unit_head", period)
            is_spouse = person("is_tax_unit_spouse", period)

            head_earnings = tax_unit.sum(adj_earnings * is_head)
            spouse_earnings = tax_unit.sum(adj_earnings * is_spouse)

            # Get EITC parameters for direct computation
            child_count = tax_unit("eitc_child_count", period)
            eitc_params = parameters(period).gov.irs.credits.eitc

            eitc_maximum = eitc_params.max.calc(child_count)
            phase_in_rate = eitc_params.phase_in_rate.calc(child_count)
            phase_out_rate = eitc_params.phase_out.rate.calc(child_count)
            # Use joint phase-out start (matching original behavior)
            phase_out_start = eitc_params.phase_out.start.calc(
                child_count
            ) + eitc_params.phase_out.joint_bonus.calc(child_count)

            # Compute head's individual EITC
            head_phased_in = min_(eitc_maximum, head_earnings * phase_in_rate)
            head_phase_out = max_(0, head_earnings - phase_out_start)
            head_reduction = phase_out_rate * head_phase_out
            head_limitation = max_(0, eitc_maximum - head_reduction)
            head_eitc = min_(head_phased_in, head_limitation)

            # Compute spouse's individual EITC
            spouse_phased_in = min_(eitc_maximum, spouse_earnings * phase_in_rate)
            spouse_phase_out = max_(0, spouse_earnings - phase_out_start)
            spouse_reduction = phase_out_rate * spouse_phase_out
            spouse_limitation = max_(0, eitc_maximum - spouse_reduction)
            spouse_eitc = min_(spouse_phased_in, spouse_limitation)

            individual_eitc = head_eitc + spouse_eitc

            # Apply AGI limit if set (0 = no limit)
            agi_limit = p.agi_eitc_limit
            agi = tax_unit("adjusted_gross_income", period)
            agi_eligible = where(agi_limit > 0, agi < agi_limit, True)

            return individual_eitc * agi_eligible * takes_up_eitc

    class reform(Reform):
        def apply(self):
            self.update_variable(eitc)

    return reform


def create_individual_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_individual_eitc()

    p = parameters.gov.contrib.individual_eitc

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_individual_eitc()
    else:
        return None


individual_eitc_reform = create_individual_eitc_reform(None, None, bypass=True)

# Backward compatibility aliases
winship_reform = individual_eitc_reform
create_eitc_winship_reform = create_individual_eitc_reform
