from policyengine_us.model_api import *


class pell_grant_head_contribution(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant head contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        dependents = person.tax_unit(
            "pell_grant_dependents_in_college", period
        )
        available_income = person("pell_grant_head_available_income", period)
        assets = person("pell_grant_contribution_from_assets", period)
        adjusted_available_income = available_income + assets
        formula = person("pell_grant_formula", period)
        uses_efc = person("pell_grant_uses_efc", period)
        uses_sai = person("pell_grant_uses_sai", period)
        p = parameters(period).gov.ed.pell_grant.head
        positive_head_contribution = p.marginal_rate.calc(
            adjusted_available_income
        )
        negative_head_contribution = max_(
            adjusted_available_income * p.negative_rate, p.min_contribution
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
        # Return amount per dependent, using a mask to avoid division by zero.
        amount_per_dependent = np.zeros_like(total)
        mask = dependents > 0
        amount_per_dependent[mask] = total[mask] / dependents[mask]

        return select([uses_efc, uses_sai], [amount_per_dependent, total])
