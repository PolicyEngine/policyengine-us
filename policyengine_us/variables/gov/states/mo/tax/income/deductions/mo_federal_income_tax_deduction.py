from policyengine_us.model_api import *


class mo_federal_income_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO Federal income tax deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=7",
        "https://revisor.mo.gov/main/OneSection.aspx?section=143.171",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Deduct a capped share of federal income tax liability.
        # Use a version that assumes no SALT deduction to avoid circularity.
        # Ignore refundable credits (including COVID-19 rebates).
        gov = parameters(period).gov
        uncapped_federal_income_tax_ignoring_credits = add(
            tax_unit,
            period,
            ["no_salt_income_tax"] + gov.irs.credits.refundable,
        )
        # Law is vague, but for now, limit to nonnegative tax.
        federal_income_tax_ignoring_credits = max_(
            0, uncapped_federal_income_tax_ignoring_credits
        )
        # Apply rate based on AGI.
        p = gov.states.mo.tax.income.deductions.federal_income_tax
        tax_unit_mo_agi = add(tax_unit, period, ["mo_adjusted_gross_income"])
        rate = p.rate.calc(tax_unit_mo_agi)
        uncapped = federal_income_tax_ignoring_credits * rate
        # Apply cap based on filing status.
        cap = p.cap[tax_unit("filing_status", period)]
        return min_(uncapped, cap)
