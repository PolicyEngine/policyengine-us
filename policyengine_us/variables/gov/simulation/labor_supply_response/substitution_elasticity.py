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
        "https://academic.oup.com/restud/article-abstract/72/2/395/1558553",
    ]

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.simulation.labor_supply_responses.elasticities.substitution

        # Check for global override
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

        # Calculate earnings
        raw_earnings = add(
            person,
            period,
            [
                "employment_income_before_lsr",
                "self_employment_income_before_lsr",
            ],
        )
        # Use max_ to prevent negative earnings from causing issues
        earnings = max_(raw_earnings, 0)
        # Use searchsorted with side='right' to bin earnings into deciles
        # This gives decile numbers 1-10 directly without needing to add 1
        earnings_decile = np.searchsorted(
            EARNINGS_DECILE_MARKERS, earnings, side="right"
        )

        # Determine if primary earner (highest earner in tax unit)
        tax_unit = person.tax_unit
        max_earnings_in_unit = tax_unit.max(earnings)
        is_primary_earner = earnings == max_earnings_in_unit

        # Get base elasticity from position and decile
        base_elasticity = np.zeros_like(earnings, dtype=float)

        # Handle zero earnings first
        zero_earnings = earnings == 0
        base_elasticity[zero_earnings] = 0

        # For non-zero earnings, assign base elasticities
        non_zero_earnings = earnings > 0

        if np.any(non_zero_earnings):
            # Primary earners by decile
            for i in range(10):  # Iterate through deciles 1-10
                decile_num = i + 1  # Decile numbers are 1-10
                mask = (
                    non_zero_earnings
                    & (earnings_decile == decile_num)
                    & is_primary_earner
                )
                if np.any(mask):
                    # Access parameter using getattr to handle both normal and test scenarios
                    decile_param = getattr(
                        p.by_position_and_decile.primary, str(decile_num)
                    )
                    # Handle both Parameter objects and raw values (when overridden in tests)
                    param_value = (
                        decile_param(period)
                        if callable(decile_param)
                        else decile_param
                    )
                    base_elasticity[mask] = param_value

            # Secondary earners get zero elasticity (only primary earners have non-zero values)

        # Apply age multiplier for individuals at or above age threshold
        age = person("age", period.this_year)
        age_multiplier = where(
            age >= p.age_threshold,
            p.age_multiplier_over_threshold,
            1.0,  # No multiplier for under threshold
        )

        return base_elasticity * age_multiplier
