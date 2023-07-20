from policyengine_us.model_api import *


class ct_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "CT EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/Schedule-CT-EITC_1222.pdf" 
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        eitc = tax_unit("earned_income_tax_credit", period)
        rate = parameters(period).gov.states.ct.tax.income.credits.eitc.refundable
        tentative_ct_eic = eitc * rate
        household_credit = tax_unit("ct_household_credit", period)
        return max_(0, tentative_ct_eic - household_credit)