from policyengine_us.model_api import *


class sc_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "SC Use Tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/resources-site/lawandpolicy/Documents/SC%20Sales%20Tax%20Manual.pdf"
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        income = tax_unit("sc_agi", period)
        county = spm_unit.household("county_str", period)
        is_group1_county = tax_unit.household("is_group_1_county", period)
        is_group2_county = tax_unit.household("is_group_2_county", period)
        is_group3_county = tax_unit.household("is_group_3_county", period)

        p = parameters(period).gov.states.sc.tax.income.use_tax.rate

        # Compute main amount, a dollar amount based on SC AGI.
        additional_rate =
         select(
            [
                is_group1_county,
                is_group2_county,
                is_group3_county,
            ],
            [
                p.group_1_rate,
                p.group_2_rate,
                p.group_3_rate,
            ],
            default = 0
        )

        # Compute use tax rate by main rate plus local county additional rate
        total_rate = p.main_rate + additional_rate

        return income * total rate
        