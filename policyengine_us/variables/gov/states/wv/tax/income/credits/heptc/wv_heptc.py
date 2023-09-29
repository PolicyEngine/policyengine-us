from policyengine_us.model_api import *


class wv_heptc(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia homestead excess property tax credit"
    defined_for = "wv_heptc_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-23/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14"
    )

    def formula(tax_unit, period, parameters):
        wv_sctc = tax_unit("wv_sctc", period)
        property_tax = tax_unit("property_tax_primary_residence", period)
        wv_ghi = tax_unit("wv_gross_household_income", period)

        p = parameters(period).gov.states.wv.tax.income.credits.heptc
        heptc_amount = property_tax - wv_sctc - p.ghi_percentage * wv_ghi

        return min_(heptc_amount, p.max_amount)
