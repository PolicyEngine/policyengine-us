from policyengine_us.model_api import *


class wv_sctc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia senior citizens tax credit"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=27 "
        "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#page=35"
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    # The senior citizens tax credit is used to calculate the Homestead access property tax credit
    # and provides a credit against property taxes as opposed to income taxes
    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        wv_homestead_exemption = tax_unit("wv_homestead_exemption", period)

        p_sctc = parameters(period).gov.states.wv.tax.income.credits.sctc
        p_homestead = parameters(
            period
        ).gov.states.wv.tax.income.exemptions.homestead_exemption

        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = p_sctc.fpg_percentage * fpg

        meets_agi_condition = federal_agi <= income_threshold
        meets_homestead_exemption_condition = (
            wv_homestead_exemption == p_homestead.max_amount
        )

        return meets_agi_condition & meets_homestead_exemption_condition
