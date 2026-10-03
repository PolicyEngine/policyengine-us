from policyengine_us.model_api import *


class tax_unit_roles_supplied(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit roles are supplied"
    documentation = "Whether every member of the tax unit has a supplied tax_unit_role_input, in which case is_tax_unit_head and is_tax_unit_spouse use the supplied roles instead of age ordering. A unit whose roles are supplied for only some members, or whose supplied roles do not name exactly one head and at most one spouse, is an error rather than a silent fallback."

    def formula(tax_unit, period, parameters):
        role = tax_unit.members("tax_unit_role_input", period)
        roles = role.possible_values
        supplied = role != roles.UNSPECIFIED
        all_supplied = tax_unit.all(supplied)
        partly_supplied = tax_unit.any(supplied) & ~all_supplied
        if partly_supplied.any():
            raise ValueError(
                f"tax_unit_role_input is supplied for some members of "
                f"{partly_supplied.sum()} tax units but not for others. "
                "Supply a role for every member of a tax unit, or for none."
            )
        heads = tax_unit.sum(role == roles.HEAD)
        spouses = tax_unit.sum(role == roles.SPOUSE)
        malformed = all_supplied & ((heads != 1) | (spouses > 1))
        if malformed.any():
            raise ValueError(
                f"tax_unit_role_input gives {malformed.sum()} tax units "
                "something other than exactly one HEAD and at most one "
                "SPOUSE."
            )
        return all_supplied
