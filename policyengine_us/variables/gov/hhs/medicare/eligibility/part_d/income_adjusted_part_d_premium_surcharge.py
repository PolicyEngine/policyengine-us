from policyengine_us.model_api import *


class income_adjusted_part_d_premium_surcharge(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part D premium surcharge (income-adjusted)"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_enrolled"
    reference = "https://www.law.cornell.edu/cfr/text/42/423.286"
    documentation = "Annualized Medicare Part D IRMAA surcharge under 42 U.S.C. 1395w-113(a)(7). This is the federally set income-related premium adjustment amount, paid in addition to the beneficiary's underlying Part D plan premium. Annual bracket values come from CMS fact sheets."

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        filing_status = tax_unit("filing_status", period)
        prior_period = period.offset(-2, "year")
        agi = tax_unit("adjusted_gross_income", prior_period)
        tax_exempt_interest = tax_unit("tax_exempt_interest_income", prior_period)
        magi = agi + tax_exempt_interest

        status = filing_status.possible_values
        statuses = [
            status.SINGLE,
            status.JOINT,
            status.HEAD_OF_HOUSEHOLD,
            status.SURVIVING_SPOUSE,
            status.SEPARATE,
        ]
        in_status = [
            filing_status == filing_status_type for filing_status_type in statuses
        ]

        p = parameters(period).gov.hhs.medicare.part_d.irmaa

        monthly_surcharge = select(
            in_status,
            [
                p.single.calc(magi),
                p.joint.calc(magi),
                p.head_of_household.calc(magi),
                p.surviving_spouse.calc(magi),
                p.separate.calc(magi),
            ],
        )

        return monthly_surcharge * MONTHS_IN_YEAR
