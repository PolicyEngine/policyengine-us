from policyengine_us.model_api import *


def _nonzero(value):
    return value != 0


def _primary_substitution_elasticities(substitution):
    primary = substitution.by_position_and_decile.primary
    return [primary._children[str(decile)] for decile in range(1, 11)]


def _labor_supply_elasticities_active(elasticities):
    income_active = _nonzero(elasticities.income.all) or _nonzero(
        elasticities.income.base
    )
    substitution_active = (
        _nonzero(elasticities.substitution.all)
        or _nonzero(elasticities.substitution.by_position_and_decile.secondary)
        or any(
            _nonzero(elasticity)
            for elasticity in _primary_substitution_elasticities(
                elasticities.substitution
            )
        )
    )
    return income_active or substitution_active


class labor_supply_behavioral_response(Variable):
    value_type = float
    entity = Person
    label = "earnings-related labor supply change"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.simulation.labor_supply_responses
        simulation = person.simulation
        if simulation.baseline is None:
            return 0  # No reform, no impact
        if not _labor_supply_elasticities_active(p.elasticities):
            return 0

        # Guard against re-entry (prevents recursion when branches calculate variables)
        if (  # pragma: no cover
            hasattr(simulation, "_lsr_calculating") and simulation._lsr_calculating
        ):
            return 0

        # Mark that we're calculating LSR
        simulation._lsr_calculating = True  # pragma: no cover

        try:  # pragma: no cover
            # Requires reform scenario with simulation branching - tested via microsim
            measurement_branch = simulation.get_branch(
                "lsr_measurement", clone_system=True
            )  # A branch without LSRs
            baseline_branch = simulation.get_branch("baseline").get_branch(
                "baseline_lsr_measurement", clone_system=True
            )  # Already created by default
            baseline_branch.tax_benefit_system.parameters.simulation = (
                measurement_branch.tax_benefit_system.parameters.simulation
            )

            # (system with LSRs) <- (system without LSRs used to calculate LSRs)
            #                      |
            #                      * -(baseline system without LSRs used to calculate LSRs)

            for branch in [measurement_branch, baseline_branch]:
                branch.tax_benefit_system.neutralize_variable(
                    "employment_income_behavioral_response"
                )
                branch.tax_benefit_system.neutralize_variable(
                    "self_employment_income_behavioral_response"
                )
                branch.set_input(
                    "employment_income_before_lsr",
                    period,
                    person("employment_income_before_lsr", period),
                )
                branch.set_input(
                    "self_employment_income_before_lsr",
                    period,
                    person("self_employment_income_before_lsr", period),
                )

            response = add(
                person,
                period,
                [
                    "income_elasticity_lsr",
                    "substitution_elasticity_lsr",
                ],
            )
            simulation = person.simulation
            del simulation.branches["baseline"].branches["baseline_lsr_measurement"]
            del simulation.branches["lsr_measurement"]

            simulation.macro_cache_read = False
            simulation.macro_cache_write = False

            return response

        finally:
            # Clear the re-entry guard
            simulation._lsr_calculating = False
