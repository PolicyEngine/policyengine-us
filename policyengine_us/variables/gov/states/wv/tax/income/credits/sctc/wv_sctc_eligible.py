from policyengine_us.model_api import *


class wv_senior_citizens_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia senior citizens tax credit"
    reference = (
        "https://code.wvlegislature.gov/11-21-21/"
        "https://tax.wv.gov/Documents/TaxForms/2021/it140.pdf#page=27 "
    )
    definition_period = YEAR
    defined_for = StateCode.WV

    # The senior citizens tax credit is used to calculate the Homestead access property tax credit
    # and provides a credit against property taxes as opposed to income taxes
    def formula(tax_unit, period, parameters):
        wv_agi = tax_unit("wv_agi", period)
        assessed_property_value = add(
            tax_unit, period, ["assessed_property_value"]
        )
        # amt_income

        p = parameters(period).gov.states.wv.tax.income.credits.sctc

        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = p.fpg_percentage * fpg

        meets_agi_condition = wv_agi <= income_threshold
        meets_home_value_condition = (
            p.home_value_threshold < assessed_property_value
        )

        return meets_agi_condition & meets_home_value_condition
