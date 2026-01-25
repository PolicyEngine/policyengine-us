from policyengine_us.model_api import *


class pell_grant_head_contribution(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant head contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        available_income = person("pell_grant_head_available_income", period)
        assets = person("pell_grant_contribution_from_assets", period)
        adjusted_available_income = available_income + assets
        formula = person("pell_grant_formula", period)
        p = parameters(period).gov.ed.pell_grant
        positive_head_contribution = p.head.marginal_rate.calc(
            adjusted_available_income
        )
        negative_head_contribution = max_(
            adjusted_available_income * p.head.negative_rate,
            p.head.min_contribution,
        )
        total_head_contribution = where(
            adjusted_available_income >= 0,
            positive_head_contribution,
            negative_head_contribution,
        )
        total = where(
            formula == formula.possible_values.B,
            adjusted_available_income,
            total_head_contribution,
        )

        if p.uses_sai:
            return total
        else:
            # EFC divides by number of dependents in college
            dependents = person.tax_unit(
                "pell_grant_dependents_in_college", period
            )
            amount_per_dependent = np.zeros_like(total)
            mask = dependents > 0
            amount_per_dependent[mask] = total[mask] / dependents[mask]
            return amount_per_dependent
