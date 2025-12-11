from policyengine_us.model_api import *


class md_local_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        in_md = tax_unit.household("state_code_str", period) == "MD"

        anne_arundel_tax = tax_unit("md_anne_arundel_county_tax", period)
        frederick_tax = tax_unit("md_frederick_county_tax", period)
        flat_rate_tax = tax_unit("md_flat_rate_county_tax", period)

        total_tax = anne_arundel_tax + frederick_tax + flat_rate_tax

        return where(in_md, total_tax, 0)
