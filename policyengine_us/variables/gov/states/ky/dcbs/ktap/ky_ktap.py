from policyengine_us.model_api import *


class ky_ktap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/",
        "https://law.justia.com/codes/kentucky/chapter-205/section-205-200/",
    )
    defined_for = "ky_ktap_eligible"

    def formula(spm_unit, period, parameters):
        # Per 921 KAR 2:016 Section 9(4):
        # Benefit = min(0.55 × deficit, payment_maximum)
        # where deficit = standard_of_need - countable_income
        #
        # Per KRS 205.200(2): "In no instance shall grants to families
        # with no income be less than the appropriate grant maximum."
        # So families with zero countable income receive payment_maximum.
        p = parameters(period).gov.states.ky.dcbs.ktap.benefit
        standard_of_need = spm_unit("ky_ktap_standard_of_need", period)
        countable_income = spm_unit("ky_ktap_countable_income", period)
        payment_maximum = spm_unit("ky_ktap_payment_maximum", period)
        deficit = max_(standard_of_need - countable_income, 0)
        calculated_benefit = min_(deficit * p.rate, payment_maximum)
        return where(
            countable_income == 0, payment_maximum, calculated_benefit
        )
