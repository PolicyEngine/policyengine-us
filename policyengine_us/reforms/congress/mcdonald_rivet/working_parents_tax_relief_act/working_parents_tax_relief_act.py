from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_working_parents_tax_relief_act() -> Reform:

    class eitc_young_child_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "EITC-qualifying young children"
        unit = "/1"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_child = person("is_qualifying_child_dependent", period)
            meets_eitc_id = person("meets_eitc_identification_requirements", period)
            is_eitc_eligible_child = is_child & meets_eitc_id
            age = person("age", period)
            p = parameters(
                period
            ).gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act
            is_young = age < p.young_child_age_threshold
            return tax_unit.sum(is_eitc_eligible_child & is_young)

    class eitc_phase_in_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-in rate"
        unit = "/1"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_child_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            baseline_rate = eitc.phase_in_rate.calc(child_count)

            p = parameters(
                period
            ).gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act
            if not p.in_effect:
                return baseline_rate

            young_child_count = min_(
                tax_unit("eitc_young_child_count", period), p.max_young_children
            )

            bonus = where(
                child_count == 1,
                where(
                    young_child_count > 0,
                    p.credit_percentage_increase_one_child,
                    0,
                ),
                young_child_count * p.credit_percentage_increase_per_young_child,
            )

            return baseline_rate + bonus

    class eitc_phase_out_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "EITC phase-out rate"
        unit = "/1"
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            eitc = parameters(period).gov.irs.credits.eitc
            num_children = tax_unit("eitc_child_count", period)
            baseline_rate = eitc.phase_out.rate.calc(num_children)

            p = parameters(
                period
            ).gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act
            if not p.in_effect:
                return baseline_rate

            young_child_count = min_(
                tax_unit("eitc_young_child_count", period), p.max_young_children
            )

            bonus = where(
                num_children >= 1,
                young_child_count * p.phaseout_percentage_increase_per_young_child,
                0,
            )

            return baseline_rate + bonus

    class eitc_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum EITC"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_child_count", period)
            eitc = parameters(period).gov.irs.credits.eitc
            baseline_max = eitc.max.calc(child_count)
            baseline_rate = eitc.phase_in_rate.calc(child_count)

            p = parameters(
                period
            ).gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act
            if not p.in_effect:
                return baseline_max

            # Per IRC §32(b): max = credit_percentage × earned_income_amount
            # Scale proportionally: new_max = baseline_max × (new_rate / baseline_rate)
            new_rate = tax_unit("eitc_phase_in_rate", period)
            ratio = where(baseline_rate > 0, new_rate / baseline_rate, 1)
            return baseline_max * ratio

    class reform(Reform):
        def apply(self):
            self.update_variable(eitc_young_child_count)
            self.update_variable(eitc_phase_in_rate)
            self.update_variable(eitc_phase_out_rate)
            self.update_variable(eitc_maximum)

    return reform


def create_working_parents_tax_relief_act_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_working_parents_tax_relief_act()

    p = parameters.gov.contrib.congress.mcdonald_rivet.working_parents_tax_relief_act
    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_working_parents_tax_relief_act()
    else:
        return None


working_parents_tax_relief_act = create_working_parents_tax_relief_act_reform(
    None, None, bypass=True
)
