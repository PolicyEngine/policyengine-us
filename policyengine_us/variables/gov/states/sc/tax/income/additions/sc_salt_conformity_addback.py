from policyengine_us.model_api import *


class sc_salt_conformity_addback(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina SALT conformity addition after the state tax addback"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    end = "2025-12-31"
    reference = (
        "https://www.scstatehouse.gov/Archives/CodeofLaws2025/t12c006.php#12-6-1130",
        "https://dor.sc.gov/income-tax-south-carolina-internal-revenue-code-conformity-update",
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=4",
    )

    def formula_2025(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        # South Carolina conforms to IRC section 164 as of December 31, 2024.
        prior_cap = parameters(
            "2024-12-31"
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]
        property_taxes = add(
            tax_unit,
            period,
            ["real_estate_taxes", "sc_federal_itemized_personal_property_taxes"],
        )
        federal_salt = tax_unit("salt_deduction", period)
        disallowed_taxes = max_(0, federal_salt - min_(property_taxes, prior_cap))

        # Line 2 of the worksheet is zero for separate filers. Other filers
        # retain the age/blind amounts and any dependent limitation.
        p = parameters(period).gov.states.sc.tax.income.additions.obbba
        basic = tax_unit("basic_standard_deduction", period)
        standard_increase = max_(
            0, basic - p.pre_obbba_standard_deduction[filing_status]
        )
        old_standard = where(
            filing_status == filing_status.possible_values.SEPARATE,
            0,
            tax_unit("standard_deduction", period) - standard_increase,
        )
        itemized = tax_unit("itemized_taxable_income_deductions", period)
        combined_addback = min_(disallowed_taxes, max_(0, itemized - old_standard))
        # SC1040 line a already restores the deductible income or sales taxes.
        line_a = tax_unit("sc_state_tax_addback", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        return where(itemizes, max_(0, combined_addback - line_a), 0)
