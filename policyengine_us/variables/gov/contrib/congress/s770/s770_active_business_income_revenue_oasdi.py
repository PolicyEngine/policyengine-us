from policyengine_us.model_api import *
from policyengine_us.reforms.congress.s770.section_8 import (
    enabled,
    allocate_bases,
    revenue_shares,
)


class s770_active_business_income_revenue_oasdi(Variable):
    value_type = float
    entity = TaxUnit
    label = "OASDI revenue from S.770 active business tax"
    documentation = "OASDI source accounting alongside tob_revenue_oasdi. Custom mode applies the component share; combined_rate_share applies the OACT combined-rate share; all_addon sends all NII add-on points; bill applies 62 percent to all resulting NIIT including the separately reported existing NIIT revenue. Transfer timing is independent of tax timing."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"

    def formula(tax_unit, period, parameters):
        return revenue_shares(parameters, period)[2] * tax_unit(
            "s770_active_business_income_tax", period
        )
