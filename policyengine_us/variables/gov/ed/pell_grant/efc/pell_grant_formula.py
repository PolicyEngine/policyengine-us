from policyengine_us.model_api import *


class PellGrantFormula(Enum):
    A = "A"
    B = "B"
    C = "C"


class pell_grant_formula(Variable):
    value_type = Enum
    possible_values = PellGrantFormula
    default_value = PellGrantFormula.A
    entity = Person
    label = "Pell Grant formula"
    definition_period = YEAR

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        count_dependents = tax_unit("tax_unit_dependents", period)
        has_dependents = count_dependents >= 1
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        in_head = is_head | is_spouse
        return select(
            [
                has_dependents & ~in_head,
                ~has_dependents & in_head,
                has_dependents & in_head,
            ],
            [PellGrantFormula.A, PellGrantFormula.B, PellGrantFormula.C],
        )
