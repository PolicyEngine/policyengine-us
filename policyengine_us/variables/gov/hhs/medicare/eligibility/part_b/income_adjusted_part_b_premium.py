from policyengine_us.model_api import *


class income_adjusted_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premium (income-adjusted)"
    unit = USD
    definition_period = YEAR
    defined_for = "is_medicare_eligible"
    reference = "https://www.medicare.gov/your-medicare-costs/part-b-costs"
    documentation = "Medicare Part B premium adjusted for income (IRMAA). Based on modified adjusted gross income from 2 years prior."

    def formula(person, period, parameters):

        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        # Medicare Part B IRMAA is based on MAGI: AGI + tax-exempt interest
        agi = tax_unit("adjusted_gross_income", period)
        tax_exempt_interest = tax_unit("tax_exempt_interest_income", period)
        income = agi + tax_exempt_interest
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

        # IRMAA amounts are monthly, multiply by MONTHS_IN_YEAR to get annual
        # Base is already annual
        annual_irmaa = irmaa_amount * MONTHS_IN_YEAR
        return base + annual_irmaa
