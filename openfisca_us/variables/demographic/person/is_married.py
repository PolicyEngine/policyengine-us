from openfisca_us.model_api import *


class is_married(Variable):
    value_type = bool
    entity = Family
    label = "Married"
    documentation = "Whether the adults in this family are married."
    definition_period = YEAR

    def formula(family, period, parameters):
        # If any tax unit is a married filer, assume the family is.
        person = family.members
        marital_status = person.tax_unit("marital_status", period)
        mars_type = marital_status.possible_values
        person_is_married = is_in(
            person.tax_unit("mars", period),
            [
                mars_type.JOINT,
                mars_type.SEPARATE,
            ],
        )
        return family.any(person_is_married)
