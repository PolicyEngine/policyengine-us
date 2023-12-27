from policyengine_us.model_api import *


class wv_homestead_excess_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the West Virginia homestead excess property tax credit"
    )
    reference = (
        "https://code.wvlegislature.gov/11-21-23/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14"
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        wv_sctc = tax_unit("wv_sctc", period)
        property_tax = tax_unit("property_tax_primary_residence", period)
        wv_ghi = tax_unit("wv_gross_household_income", period)
        wv_tax_unit_fpg = tax_unit("tax_unit_fpg", period)
        p = parameters(period).gov.states.wv.tax.income.credits.heptc.rate
        low_income_guidelines = p.fpg * wv_tax_unit_fpg
        lig_eligible = federal_agi <= low_income_guidelines
        property_tax_value = property_tax - wv_sctc
        ghi_amount = p.household_income * wv_ghi
        property_tax_eligible = property_tax_value > ghi_amount
        return lig_eligible & property_tax_eligible
