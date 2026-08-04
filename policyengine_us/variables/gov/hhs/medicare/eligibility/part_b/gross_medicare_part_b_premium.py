from policyengine_us.model_api import *


class gross_medicare_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Gross Medicare Part B premium"
    unit = USD
    definition_period = YEAR
    defined_for = "is_medicare_eligible"
    reference = "https://www.medicare.gov/your-medicare-costs/part-b-costs"
    documentation = "Annual Medicare Part B premium before Medicare Savings Program coverage, including any income-related monthly adjustment amount. Based on modified adjusted gross income from 2 years prior."

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filing_status_holder = tax_unit.simulation.get_holder("filing_status")
        filing_status = tax_unit("filing_status", period)
        status = filing_status_holder.variable.possible_values
        is_single = filing_status == status.SINGLE
        is_joint = filing_status == status.JOINT
        is_head_of_household = filing_status == status.HEAD_OF_HOUSEHOLD
        is_surviving_spouse = filing_status == status.SURVIVING_SPOUSE
        is_separated = filing_status == status.SEPARATE
        magi = tax_unit("medicare_irmaa_magi_two_years_prior", period)
        base = person("base_part_b_premium", period)

        p = parameters(period).gov.hhs.medicare.part_b.irmaa

        irmaa_amount = select(
            [
                is_single,
                is_joint,
                is_head_of_household,
                is_surviving_spouse,
                is_separated,
            ],
            [
                p.single.calc(magi),
                p.joint.calc(magi),
                p.head_of_household.calc(magi),
                p.surviving_spouse.calc(magi),
                p.separate.calc(magi),
            ],
        )

        # IRMAA amounts are monthly, multiply by MONTHS_IN_YEAR to get annual.
        # Base is already annual.
        annual_irmaa = irmaa_amount * MONTHS_IN_YEAR
        return base + annual_irmaa
