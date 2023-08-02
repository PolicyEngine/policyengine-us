from policyengine_us.model_api import *


class pell_grant_efc(Variable):
    value_type = float
    entity = Person
    label = "Expected Family Contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        head_contribution = person("pell_grant_head_contribution", period)
        dependent_contribution = person(
            "pell_grant_dependent_contribution", period
        )
        head_income = person("pell_grant_head_income", period)
        formula = person("pell_grant_formula", period).decode_to_str()
        zero_efc_max = parameters(period).gov.ed.pell_grant.efc.automatic_zero
        return select(
            [formula == "A", formula == "B", formula == "C"],
            [
                where(
                    head_income <= zero_efc_max,
                    0,
                    head_contribution + dependent_contribution,
                ),
                head_contribution,
                where(head_income <= zero_efc_max, 0, head_contribution),
            ],
        )
