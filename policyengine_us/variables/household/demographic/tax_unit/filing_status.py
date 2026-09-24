from policyengine_us.model_api import *


class FilingStatus(Enum):
    SINGLE = "Single"
    JOINT = "Joint"
    SEPARATE = "Separate"
    HEAD_OF_HOUSEHOLD = "Head of household"
    SURVIVING_SPOUSE = "Surviving spouse"


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
        disagrees = is_supplied & ((supplied == statuses.JOINT) != married)
        if disagrees.any():
            raise ValueError(
                f"filing_status_input disagrees with the members of "
                f"{disagrees.sum()} tax units: a supplied JOINT status needs a "
                "spouse in the unit, and a unit with a spouse must be supplied "
                "JOINT."
            )
        return select(
            [supplied == statuses[status.name] for status in FilingStatus],
            list(FilingStatus),
            default=derived,
        )
