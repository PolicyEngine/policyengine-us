from policyengine_us.model_api import *


class wv_homestead_excess_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia homestead excess property tax credit"
    defined_for = "wv_homestead_excess_property_tax_credit_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-23/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=13"
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=14"
    )

    def formula(tax_unit, period, parameters):
        wv_sctc = tax_unit(
            "wv_sctc", period
        )  # West Virginia homestead excess property tax credit
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        wv_ghi = tax_unit("wv_gross_household_income", period)

        p = parameters(period).gov.states.wv.tax.income.credits.heptc
        heptc_amount = max_(
            property_tax - wv_sctc - p.rate.household_income * wv_ghi, 0
        )

        return min_(heptc_amount, p.cap)
