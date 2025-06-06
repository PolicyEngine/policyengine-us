from policyengine_us.model_api import *


class income_adjusted_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premium (income-adjusted)"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # Gate: only Medicare-eligible people pay anything
        is_eligible = person("is_medicare_eligible", period)

        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        income = tax_unit("employment_income", period)
        base = person("base_part_b_premium", period)

        # Build boolean masks for each status
        status = filing_status.possible_values
        statuses = [
            status.SINGLE,
            status.JOINT,
            status.HEAD_OF_HOUSEHOLD,
            status.SURVIVING_SPOUSE,
            status.SEPARATE,
        ]
        in_status = [filing_status == s for s in statuses]

        p = parameters(period).gov.hhs.medicare.part_b.irmaa

        irmaa_amount = select(
            in_status,
            [
                p.single.calc(income),
                p.joint.calc(income),
                p.head_of_household.calc(income),
                p.surviving_spouse.calc(income),
                p.separate.calc(income),
            ],
        )

        return is_eligible * (base + irmaa_amount)
