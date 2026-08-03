from policyengine_us.model_api import *


class mo_wftc_liability_cap(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri Working Families Tax Credit liability cap"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=43",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.177&bid=49978&hl=",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Form MO-WFTC Lines 7-9 cap the Working Families Tax Credit at
        # MO-1040 Line 36 tax less Line 42 (Form MO-TC miscellaneous
        # credits, not modeled) and Line 43 (the property tax credit),
        # per RSMo 143.177.3: the credit applies "after reduction for
        # all other credits allowed thereon."
        tax_before_credits = add(tax_unit, period, ["mo_income_tax_before_credits"])
        property_tax_credit = tax_unit("mo_property_tax_credit", period)
        return max_(tax_before_credits - property_tax_credit, 0)
