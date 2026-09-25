from policyengine_us.model_api import *


class FilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    SURVIVING_SPOUSE = "Surviving spouse"


# The eligibility rule behind each status that a reform can switch off.
STATUS_RULES = {
    FilingStatus.HEAD_OF_HOUSEHOLD: "head_of_household_eligible",
    FilingStatus.SURVIVING_SPOUSE: "surviving_spouse_eligible",
}


def _rule_switched_off(tax_unit, period, parameters, variable_name):
    # The same test policyengine-core applies before calculating a variable:
    # a structural reform neutralized it, or its abolition parameter is set.
    variable = tax_unit.simulation.tax_benefit_system.variables[variable_name]
    abolished = parameters(period).gov.abolitions[variable_name]
    return variable.is_neutralized or bool(abolished)


class filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    definition_period = YEAR
    label = "Filing status for the tax unit"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Separation can make the taxpayer file separately only when it applies
        # to the tax unit head or spouse, not a dependent or other member.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_separated = tax_unit.any(is_head_or_spouse & person("is_separated", period))
        married = tax_unit("tax_unit_married", period)
        derived = select(
            [
                married,
                tax_unit("surviving_spouse_eligible", period),
                tax_unit("head_of_household_eligible", period),
                is_separated,
            ],
            [
                FilingStatus.JOINT,
                FilingStatus.SURVIVING_SPOUSE,
                FilingStatus.HEAD_OF_HOUSEHOLD,
                FilingStatus.SEPARATE,
            ],
            default=FilingStatus.SINGLE,
        )
        # A dataset's tax-unit constructor can supply the status instead.
        supplied = tax_unit("filing_status_input", period)
        statuses = supplied.possible_values
        is_supplied = supplied != statuses.UNSPECIFIED
        # Check a supplied status against the supplied roles themselves where
        # the unit has them, so no reform to the role variables can turn this
        # data check into an error.
        role = person("tax_unit_role_input", period)
        roles = role.possible_values
        roles_supplied = tax_unit.all(role != roles.UNSPECIFIED)
        has_spouse = where(roles_supplied, tax_unit.any(role == roles.SPOUSE), married)
        disagrees = is_supplied & ((supplied == statuses.JOINT) != has_spouse)
        if disagrees.any():
            raise ValueError(
                f"filing_status_input disagrees with the members of "
                f"{disagrees.sum()} tax units: a supplied JOINT status needs a "
                "spouse in the unit, and a unit with a spouse must be supplied "
                "JOINT."
            )
        # A reform that switches off a status's rule re-derives the units
        # supplied with that status; every other supplied status stands.
        honored = [
            status
            for status in FilingStatus
            if status not in STATUS_RULES
            or not _rule_switched_off(
                tax_unit, period, parameters, STATUS_RULES[status]
            )
        ]
        return select(
            [supplied == statuses[status.name] for status in honored],
            honored,
            default=derived,
        )
