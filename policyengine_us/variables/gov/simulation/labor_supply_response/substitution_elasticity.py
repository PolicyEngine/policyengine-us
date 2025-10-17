from policyengine_us.model_api import *


class substitution_elasticity(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR
    reference = [
        "https://www.cbo.gov/publication/43675",
        "https://www.cbo.gov/publication/43676",
    ]

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
            [
                "employment_income_before_lsr",
                "self_employment_income_before_lsr",
            ],
        )
        earnings = max_(raw_earnings, 0)
        earnings_decile = (
            np.searchsorted(EARNINGS_DECILE_MARKERS, earnings) + 1
        )

        tax_unit = person.tax_unit
        # Primary earner == highest earner in tax unit
        max_earnings_in_unit = tax_unit.max(earnings)
        is_primary_earner = earnings == max_earnings_in_unit

        # Get age for age-based elasticities
        age = person("age", period.this_year)
        is_65_or_over = age >= 65

        elasticities = np.zeros_like(earnings)

        # Handle zero earnings first
        zero_earnings = earnings == 0
        elasticities[zero_earnings] = 0

        # For non-zero earnings, assign elasticities based on age
        non_zero_earnings = earnings > 0

        if np.any(non_zero_earnings):
            # Get age-specific parameter groups
            p_under_65 = p.by_age_position_and_decile.under_65
            p_65_and_over = p.by_age_position_and_decile["65_and_over"]

            # Assign elasticities for under 65 group
            mask_under_65 = non_zero_earnings & ~is_65_or_over
            if np.any(mask_under_65):
                # Primary earners under 65
                decile_elasticities_under_65 = [
                    p_under_65.primary._children[str(i + 1)]
                    for i in range(10)
                ]
                for i in range(10):
                    mask = (
                        mask_under_65
                        & (earnings_decile == i + 1)
                        & is_primary_earner
                    )
                    elasticities[mask] = decile_elasticities_under_65[i]

                # Secondary earners under 65
                secondary_mask_under_65 = mask_under_65 & ~is_primary_earner
                elasticities[secondary_mask_under_65] = p_under_65.secondary

            # Assign elasticities for 65 and over group
            mask_65_and_over = non_zero_earnings & is_65_or_over
            if np.any(mask_65_and_over):
                # Primary earners 65 and over
                decile_elasticities_65_and_over = [
                    p_65_and_over.primary._children[str(i + 1)]
                    for i in range(10)
                ]
                for i in range(10):
                    mask = (
                        mask_65_and_over
                        & (earnings_decile == i + 1)
                        & is_primary_earner
                    )
                    elasticities[mask] = decile_elasticities_65_and_over[i]

                # Secondary earners 65 and over
                secondary_mask_65_and_over = (
                    mask_65_and_over & ~is_primary_earner
                )
                elasticities[secondary_mask_65_and_over] = (
                    p_65_and_over.secondary
                )

        return elasticities
