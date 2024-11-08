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
        out_of_state_purchases = tax_unit(
            "out_of_state_purchase_value", period
        )
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

        # Compute main amount, a dollar amount based on out of state purchase.
        additional_rate = select(
            [
                sc_use_tax_in_group_one_county,
                sc_use_tax_in_group_two_county,
                sc_use_tax_in_group_three_county,
            ],
            [
                p.group_one,
                p.group_two,
                p.group_three,
            ],
            # Some counties are excluded from the additional use tax
            default=0,
        )

        # Compute use tax rate by main rate plus local county additional rate
        total_rate = p.main + additional_rate

        return out_of_state_purchases * total_rate


