from policyengine_us.model_api import *


class ok_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/past-year/2021/511-Pkt-2021.pdf"
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-Pkt.pdf"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        # follows Schedule 511-D in references:
        # ... calculate pre-limit OK itemized deductions
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        capped_property_taxes = tax_unit("capped_property_taxes", period)
        ok_itm_deds = itm_deds_less_salt + capped_property_taxes
        # ... apply partial limit on OK itemized deductions
        EXEMPT_ITEMS = [
            "medical_expense_deduction",
            "charitable_deduction",
        ]
        exempt_deds = add(tax_unit, period, EXEMPT_ITEMS)
        net_deds = max_(0, ok_itm_deds - exempt_deds)
        p = parameters(period).gov.states.ok.tax.income
        limited_net_deds = min_(net_deds, p.deductions.itemized.limit)
        return exempt_deds + limited_net_deds
