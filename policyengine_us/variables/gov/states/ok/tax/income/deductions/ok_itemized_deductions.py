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
        # follows Schedule 511-D in references
        itemizing = tax_unit("tax_unit_itemizes", period)
        # calculate US itemized deductions less state non-property taxes
        us_p = parameters(period).gov.irs.deductions
        items = [
            deduction
            for deduction in us_p.itemized_deductions
            if deduction not in ["salt_deduction"]
        ]
        us_itm_deds_less_salt = add(tax_unit, period, items)
        filing_status = tax_unit("filing_status", period)
        capped_property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            us_p.itemized.salt_and_real_estate.cap[filing_status],
        )
        ok_itm_deds = us_itm_deds_less_salt + capped_property_taxes
        # apply partial limit on OK itemized deductions
        EXEMPT_ITEMS = [
            "medical_expense_deduction",
            "charitable_deduction",
        ]
        exempt_deds = add(tax_unit, period, EXEMPT_ITEMS)
        net_deds = max_(0, ok_itm_deds - exempt_deds)
        ok_p = parameters(period).gov.states.ok.tax.income.deductions
        limited_net_deds = min_(net_deds, ok_p.itemized.limit)
        return itemizing * (exempt_deds + limited_net_deds)
