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
    documentation = "The person's role in their tax unit - head, spouse or dependent - as assigned by the tax-unit constructor that built a dataset, such as the Microcosm US build. When every member of a tax unit has a supplied role, is_tax_unit_head and is_tax_unit_spouse use it, so the constructor's head, its spouse pairing and its dependency claims all hold: a younger reference person can head a couple, an adult student stays a dependent, and a minor living without a parent can head a return. The roles only say who is head, spouse or dependent; filing_status is still computed from the unit's members and the filing rules. UNSPECIFIED (the default) means the role was not supplied, and the role variables fall back to age ordering: the oldest adult is the head, skipping adults input as tax unit dependents unless every adult in the unit is one, except that the older member of a couple sharing a two-person marital unit in the tax unit heads it. The spouse is the head's partner in their marital unit; a head without one takes the next-oldest such adult who doesn't meet the qualifying child age test against the head (under 19, or under 24 if a full-time student, and younger than the head, or permanently and totally disabled). No spouse is inferred when the head or selected spouse candidate is separated. When marital units are omitted, everyone shares one marital unit, so plain age order applies."
