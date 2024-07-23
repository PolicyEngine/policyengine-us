from policyengine_us.model_api import *


class pell_grant_efc(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Pell Grant expected family contribution"
    definition_period = YEAR

    def formula(person, period, parameters):
        head_contribution = person("pell_grant_head_contribution", period)
        dependent_contribution = person(
            "pell_grant_dependent_contribution", period
        )
        head_income = person.tax_unit("pell_grant_primary_income", period)
        formula = person("pell_grant_formula", period).decode_to_str()
        zero_efc_max = parameters(period).gov.ed.pell_grant.efc.automatic_zero
        automatic_zero = head_income <= zero_efc_max
        return select(
            [formula == "A", formula == "B", formula == "C"],
            [
                where(
                    automatic_zero,
                    0,
                    max_(0, head_contribution + dependent_contribution),
                ),
                max_(0, head_contribution),
                where(automatic_zero, 0, max_(0, head_contribution)),
            ],
        )
