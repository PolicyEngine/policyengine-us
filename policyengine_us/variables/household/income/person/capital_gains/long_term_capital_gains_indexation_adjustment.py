from policyengine_us.model_api import *


class long_term_capital_gains_indexation_adjustment(Variable):
    value_type = float
    entity = Person
    label = "long-term capital gains basis indexation adjustment"
    unit = USD
    documentation = (
        "Person-level allocation of tax-unit long-term capital gains basis indexation."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        tax_unit_adjustment = tax_unit(
            "tax_unit_long_term_capital_gains_indexation_adjustment", period
        )
        gains = person("long_term_capital_gains_before_response", period)
        tax_unit_gains = add(
            tax_unit, period, ["long_term_capital_gains_before_response"]
        )
        positive_gains = max_(gains, 0)
        absolute_gains = abs(gains)
        weights = where(tax_unit_gains > 0, positive_gains, absolute_gains)
        tax_unit_weights = tax_unit.sum(weights)
        share = np.divide(
            weights,
            tax_unit_weights,
            out=np.zeros_like(weights),
            where=tax_unit_weights != 0,
        )
        return tax_unit_adjustment * share
