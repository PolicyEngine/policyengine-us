from policyengine_us.model_api import *


class ct_c4k(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = "ct_c4k_eligible"
    label = "Connecticut Care 4 Kids subsidy amount"
    reference = (
        "https://eregulations.ct.gov/eRegsPortal/Browse/RCSA/Title_17bSubtitle_17b-749Section_17b-749-13/",
        "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/",
    )

    def formula(spm_unit, period, parameters):
        weekly_rate_total = add(spm_unit, period, ["ct_c4k_payment_rate"])
        monthly_approved_cost = weekly_rate_total * WEEKS_IN_YEAR / MONTHS_IN_YEAR

        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        capped_cost = min_(monthly_approved_cost, actual_expenses)

        family_fee = spm_unit("ct_c4k_family_fee", period)
        return max_(capped_cost - family_fee, 0)
