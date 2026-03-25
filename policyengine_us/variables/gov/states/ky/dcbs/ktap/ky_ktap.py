from policyengine_us.model_api import *


class ky_ktap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=54926",
    )
    defined_for = "ky_ktap_eligible"

    def formula(spm_unit, period, parameters):
        # Per KRS 205.200(2): families with zero countable income
        # receive the payment maximum.
        p = parameters(period).gov.states.ky.dcbs.ktap.benefit
        standard_of_need = spm_unit("ky_ktap_standard_of_need", period)
        countable_income = spm_unit("ky_ktap_countable_income", period)
        payment_maximum = spm_unit("ky_ktap_payment_maximum", period)
        deficit = max_(standard_of_need - countable_income, 0)
        calculated_benefit = min_(deficit * p.rate, payment_maximum)
        return where(countable_income == 0, payment_maximum, calculated_benefit)
