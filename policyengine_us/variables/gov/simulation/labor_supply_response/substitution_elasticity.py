from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.labor_supply_response.helpers import pos


class substitution_elasticity(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR

    def formula(person, period, parameters):
        gov = parameters(period).gov
        elasticities_p = (
            gov.simulation.labor_supply_responses.elasticities.substitution
        )

        if elasticities_p.all != 0:
            return elasticities_p.all

        earnings_decile_markers = [  # Parametrise
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

        earnings = pos(person("employment_income_before_lsr", period) + person(
            "self_employment_income_before_lsr", period
        ))
        earnings_decile = (
            np.searchsorted(earnings_decile_markers, earnings) + 1
        )

        tax_unit_earnings = person.tax_unit.sum(earnings)
        # Primary earner == highest earner in tax unit
        is_primary_earner = tax_unit_earnings == person.tax_unit.max(earnings)

        elasticities = np.zeros_like(earnings)

        # If earnings are zero, return zero elasticity
        zero_earnings_mask = earnings == 0
        if np.any(zero_earnings_mask):
            elasticities[zero_earnings_mask] = 0

        # Only process non-zero earnings
        non_zero_mask = earnings > 0
        if np.any(non_zero_mask):
            p = elasticities_p.by_position_and_decile
            elasticities[non_zero_mask & ~is_primary_earner] = p.secondary
            decile_elasticities = [
                p.primary._children[str(i + 1)] for i in range(10)
            ]
            for i in range(10):
                mask = non_zero_mask & (earnings_decile == i + 1) & is_primary_earner
                elasticities[mask] = decile_elasticities[i]

        return elasticities