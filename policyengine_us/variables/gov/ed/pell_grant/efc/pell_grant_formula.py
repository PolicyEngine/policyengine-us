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
        has_dependents = person.tax_unit("tax_unit_dependents", period) > 0
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = is_head | is_spouse
        return select(
            [
                has_dependents & ~head_or_spouse,
                ~has_dependents & head_or_spouse,
            ],
            [PellGrantFormula.A, PellGrantFormula.B],
            # C formula applies for `has_dependents & head_or_spouse`.
            # Technically this also catches `~has_dependents & ~head_or_spouse`
            # but that's not a valid combination.
            default=PellGrantFormula.C,
        )
