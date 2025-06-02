from policyengine_us.model_api import *


class base_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = ""
    unit = USD
    documentation = "Medicare Part B Premium."
    definition_period = YEAR

    def formula(person, period, parameters):
        is_eligible = person("is_medicare_eligible", period)
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)

        # Get filing status breakdown
        status = filing_status.possible_values
        statuses = [
            status.SINGLE,
            status.JOINT,
            status.HEAD_OF_HOUSEHOLD,
            status.SURVIVING_SPOUSE,
            status.SEPARATE,
        ]
        in_each_status = [filing_status == s for s in statuses]

        # Get parameter structure
        brackets = parameters(period).gov.hhs.medicare.part_b.income_brackets

        # Get base premium (first bracket amount) for each filing status
        base_premium = select(
            in_each_status,
            [
                brackets.single.calc(0),
                brackets.joint.calc(0),
                brackets.single.calc(0),  # HOH uses single brackets
                brackets.single.calc(
                    0
                ),  # Surviving spouse uses single brackets
                brackets.single.calc(
                    0
                ),  # Separate uses single brackets (no separate file exists)
            ],
        )

        return is_eligible * base_premium
