from policyengine_us.model_api import *


class wv_senior_citizens_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the West Virginia senior citizens tax credit"
    definition_period = YEAR
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        wv_agi = tax_unit("wv_agi", period)
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        # amt_income

        p = parameters(period).gov.states.wv.tax.income.credits.sctc

        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = p.fpg_percentage * fpg

        return (wv_agi <= income_threshold) & (p.home_value > property_value)
