from policyengine_us.model_api import *


class sc_use_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "SC Use Tax"
    unit = USD
    definition_period = YEAR
    reference = 
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        income = tax_unit("sc_agi", period)
        county = spm_unit.household("county_str", period)
        is_group1_county = tax_unit.household("is_group_1_county", period)
        is_group2_county = tax_unit.household("is_group_2_county", period)
        is_group3_county = tax_unit.household("is_group_3_county", period)
        is_group4_county = tax_unit.household("is_group_4_county", period)

        p = parameters(period).gov.states.sc.tax.income.use_tax.rate
        # Compute main amount, a dollar amount based on SC AGI.
        main_amount = p.rate * income
        # Compute additional local use tax by county
        additional_amount = 
        