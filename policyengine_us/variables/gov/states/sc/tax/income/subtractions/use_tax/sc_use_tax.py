from policyengine_us.model_api import *


class sc_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina Use Tax"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.sc.gov/resources-site/lawandpolicy/Documents/SC%20Sales%20Tax%20Manual.pdf"
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        income = tax_unit("sc_agi", period)
        county = tax_unit.household("county_str", period)
        sc_use_tax_in_group_one_county = tax_unit.household(
            "sc_use_tax_in_group_one_county", period
        )
        sc_use_tax_in_group_two_county = tax_unit.household(
            "sc_use_tax_in_group_two_county", period
        )
        sc_use_tax_in_group_three_county = tax_unit.household(
            "sc_use_tax_in_group_three_county", period
        )

        p = parameters(period).gov.states.sc.tax.income.use_tax

        # Compute main amount, a dollar amount based on SC AGI.
        additional_rate = select(
            [
                sc_use_tax_in_group_one_county,
                sc_use_tax_in_group_two_county,
                sc_use_tax_in_group_three_county,
            ],
            [
                p.rate.group_one,
                p.rate.group_two,
                p.rate.group_three,
            ],
            default=0,
        )

        # Compute use tax rate by main rate plus local county additional rate
        total_rate = p.rate.main + additional_rate

        return income * total_rate
