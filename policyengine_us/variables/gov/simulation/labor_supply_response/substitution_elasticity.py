from policyengine_us.model_api import *


class substitution_elasticity(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.simulation.labor_supply_responses.elasticities.substitution

        if p.all != 0:
            return p.all

        # TODO: Parametrise
        EARNINGS_DECILE_MARKERS = [
            0,
            14e3,
            28e3,
            39e3,
            50e3,
            61e3,
            76e3,
            97e3,
            138e3,
            1_726e3,
        ]

        raw_earnings = add(
            person,
            period,
            ["employment_income_before_lsr", "self_employment_income_before_lsr"],
        )
        earnings = max_(raw_earnings, 0)
        earnings_decile = np.searchsorted(EARNINGS_DECILE_MARKERS, earnings) + 1

        tax_unit = person.tax_unit
        tax_unit_earnings = tax_unit.sum(earnings)
        # Primary earner == highest earner in tax unit
        is_primary_earner = tax_unit_earnings == tax_unit.max(earnings)

        elasticities = np.zeros_like(earnings)

        # First assign primary earner elasticities by decile
        decile_elasticities = [
            p.by_position_and_decile.primary._children[str(i + 1)] for i in range(10)
        ]
        for i in range(10):
            elasticities[earnings_decile == i + 1] = decile_elasticities[i]

        # Then override with secondary earner elasticity where applicable
        elasticities[~is_primary_earner] = p.by_position_and_decile.secondary

        # Zero out elasticity for zero earnings only (override assignments for zero earnings)
        zero_earnings = earnings == 0
        elasticities[zero_earnings] = 0

        return elasticities
