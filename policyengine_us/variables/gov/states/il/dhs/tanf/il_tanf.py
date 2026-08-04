from policyengine_us.model_api import *


class il_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.250",
        # IDHS PM 10-01-02 Minimum Payment (WAG 10-01-02):
        # "Regular monthly TANF benefits and Initial Prorated Entitlement
        #  (IPE) payments are rounded down to the nearest whole dollar."
        # "TANF payments of less than $1 are not made. When the monthly
        #  benefit amount would be less than $1, eligibility for cash does not
        #  exist."
        "https://www.dhs.state.il.us/page.aspx?item=15820",
    )
    defined_for = "il_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_level = spm_unit("il_tanf_payment_level_for_grant_calculation", period)
        countable_income = spm_unit(
            "il_tanf_countable_income_for_grant_calculation", period
        )
        benefit = max_(payment_level - countable_income, 0)
        benefit = min_(benefit, payment_level)
        # Regular monthly TANF benefits are rounded down to the nearest whole
        # dollar.
        benefit = np.floor(benefit)
        # Payments below the minimum ($1) are not made.
        minimum_payment = parameters(period).gov.states.il.dhs.tanf.minimum_payment
        return where(benefit >= minimum_payment, benefit, 0)
