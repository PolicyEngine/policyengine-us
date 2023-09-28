from policyengine_us.model_api import *


class wv_heptc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia homestead excess property tax credit"
    reference = (
        "https://code.wvlegislature.gov/11-21-23/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14"
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        n = tax_unit("tax_unit_size", period)
        wv_sctc = tax_unit("wv_sctc", period)
        real_property_tax = tax_unit("real_estate_taxes", period)

        p = parameters(period).gov.states.wv.tax.income.credits.heptc
        p_lig = p.low_income_guidelines
        low_income_guidelines =  p_lig.first_person + p_lig.additional_person * (n - 1)
        lig_condition = (federal_agi <= low_income_guidelines)
        real_property_tax_condition = (real_property_tax - wv_sctc) > p.ghi_percentage * Gross household income #Gross household income
        return lig_condition & real_property_tax_condition
