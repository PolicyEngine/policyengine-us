from policyengine_us.model_api import *


class taxable_income_less_qbid(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income (not considering QBID)"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#e_1",
        # P.L. 119-21, sec. 70111(b)(1), adds "without regard to section 68"
        # to section 199A(e)(1) from 2026.
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.irs.deductions
        # Section 199A(e)(1) computes taxable income without regard to
        # section 68 once P.L. 119-21 rewrites section 68, so itemizers
        # deduct their itemized deductions before that limitation.
        if p.itemized.limitation.obbb.applies:
            itemized = "total_itemized_taxable_income_deductions"
        else:
            itemized = "itemized_taxable_income_deductions"
        ded_if_itemizing = [
            itemized if deduction == "itemized_taxable_income_deductions" else deduction
            for deduction in p.deductions_if_itemizing
            if deduction != "qualified_business_income_deduction"
        ]
        ded_if_not_itemizing = [
            deduction
            for deduction in p.deductions_if_not_itemizing
            if deduction != "qualified_business_income_deduction"
        ]
        ded_value_if_itemizing = add(tax_unit, period, ded_if_itemizing)
        ded_value_if_not_itemizing = add(tax_unit, period, ded_if_not_itemizing)
        itemizes = tax_unit("tax_unit_itemizes", period)
        ded_value = where(
            itemizes,
            ded_value_if_itemizing,
            ded_value_if_not_itemizing,
        )
        return max_(0, agi - ded_value)
