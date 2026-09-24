from policyengine_us.model_api import *


class TaxUnitRole(Enum):
    UNSPECIFIED = "Unspecified"
    HEAD = "Head"
    SPOUSE = "Spouse"
    DEPENDENT = "Dependent"


class tax_unit_role_input(Variable):
    value_type = Enum
    entity = Person
    possible_values = TaxUnitRole
    default_value = TaxUnitRole.UNSPECIFIED
    definition_period = YEAR
    label = "Supplied tax unit role"
    documentation = "The person's role in their tax unit - head, spouse or dependent - as assigned by the tax-unit constructor that built a dataset, such as the Populace US build. When every member of a tax unit has a supplied role, is_tax_unit_head and is_tax_unit_spouse use it, so the constructor's head, its spouse pairing and its dependency claims all hold: a younger reference person can head a couple, an adult student stays a dependent, and a minor living without a parent can head a return. UNSPECIFIED (the default) means the role was not supplied, and the role variables fall back to age ordering, where the oldest adult is the head and the next-oldest adult the spouse."
