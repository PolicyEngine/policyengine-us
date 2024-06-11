from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.pell_grant.pell_grant_formula import PellGrantFormula


def _total_contribution(person, period, parameters):
    available_income = person("pell_grant_head_available_income", period)
    assets = person("pell_grant_contribution_from_assets", period)
    adjusted_available_income = available_income + assets
    formula = person("pell_grant_formula", period)
    p = parameters(period).gov.ed.pell_grant.efc.head
    positive_head_contribution = p.marginal_rate.calc(adjusted_available_income)
    negative_head_contribution = max_(adjusted_available_income * p.negative_rate, p.min_contribution)
    total_head_contribution = where(
        adjusted_available_income >= 0,
        positive_head_contribution,
        negative_head_contribution,
    )
    return where(formula == PellGrantFormula.B, adjusted_available_income, total_head_contribution)


class pell_grant_head_contribution(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant head contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        dependents = person.tax_unit("pell_grant_dependents_in_college", period)
        total = _total_contribution(person, period, parameters)
        # Return amount per dependent, using a mask to avoid division by zero.
        amount_per_dependent = np.zeros_like(total)
        mask = dependents > 0
        amount_per_dependent[mask] = total[mask] / dependents[mask]
        return amount_per_dependent

    def formula_2024(person, period, parameters):
        return _total_contribution(person, period, parameters)
