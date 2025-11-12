from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_exemption_reform() -> Reform:
    class ri_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Rhode Island eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.dependent_exemption

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Apply age limit if in effect
            if p.age_limit.in_effect:
                age_threshold = p.age_limit.threshold
                eligible_dependents = is_dependent & (age < age_threshold)
            else:
                eligible_dependents = is_dependent

            return tax_unit.sum(eligible_dependents)

    class ri_dependent_exemption_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island dependent exemption maximum before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.dependent_exemption

            dependents_count = tax_unit("ri_eligible_dependents_count", period)
            return dependents_count * p.amount

    class ri_dependent_exemption_phaseout(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island dependent exemption phaseout amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ri.dependent_exemption

            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("ri_agi", period)

            threshold = p.phaseout.threshold[filing_status]
            excess_income = max_(agi - threshold, 0)
            return excess_income * p.phaseout.rate

    class ri_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):

            maximum = tax_unit("ri_dependent_exemption_maximum", period)
            phaseout = tax_unit("ri_dependent_exemption_phaseout", period)

            return max_(maximum - phaseout, 0)

    class ri_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "ri_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class ri_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.ri.tax.income.exemption

            # Calculate personal exemptions base amount
            filing_status = tax_unit("filing_status", period)
            older_dependents = tax_unit("ri_older_dependents_count", period)
            personal_exemptions = (
                where(
                    filing_status == filing_status.possible_values.JOINT,
                    2,
                    1,
                )
                + older_dependents
            )
            personal_exemption_base = personal_exemptions * p_base.amount

            # Apply baseline phase-out to personal exemptions
            mod_agi = tax_unit("ri_agi", period)
            excess_agi = max_(0, mod_agi - p_base.reduction.start)
            increments = np.ceil(excess_agi / p_base.reduction.increment)
            reduction_rate = min_(p_base.reduction.rate * increments, 1)
            personal_exemption_amount = personal_exemption_base * (
                1 - reduction_rate
            )

            # Add dependent exemption (has its own phase-out logic)
            dependent_exemption_amount = tax_unit(
                "ri_dependent_exemption", period
            )

            return personal_exemption_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_eligible_dependents_count)
            self.update_variable(ri_dependent_exemption_maximum)
            self.update_variable(ri_dependent_exemption_phaseout)
            self.update_variable(ri_dependent_exemption)
            self.update_variable(ri_exemptions)
            self.update_variable(ri_older_dependents_count)

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
