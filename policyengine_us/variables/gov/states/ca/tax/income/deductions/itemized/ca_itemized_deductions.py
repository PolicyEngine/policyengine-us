from policyengine_us.model_api import *


class ca_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "California itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html"
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        itm_deds_max = itm_deds_less_salt + uncapped_property_taxes
        # compute high-AGI limit on itemized deductions
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized
        # ... determine part of itemized deductions subject to limit
        excluded_itm_deds = add(tax_unit, period, p.limit.excluded_deductions)
        included_itm_deds = p.limit.ded_fraction * max_(
            0, itm_deds_max - excluded_itm_deds
        )
        # ... determine limit amount
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        agi_limit = p.limit.agi_fraction * max_(
            0, agi - p.limit.agi_threshold[filing_status]
        )
        limit_amount = min_(included_itm_deds, agi_limit)
        # return limited itemized deductions
        return max_(0, itm_deds_max - limit_amount)
