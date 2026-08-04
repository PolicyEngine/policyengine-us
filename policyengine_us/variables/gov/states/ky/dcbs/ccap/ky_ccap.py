from policyengine_us.model_api import *


class ky_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kentucky CCAP benefit amount"
    definition_period = MONTH
    defined_for = "ky_ccap_eligible"
    reference = (
        "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=10",
        "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=11",
    )

    def formula(spm_unit, period, parameters):
        # 922 KAR 2:160 Section 10-11: the net subsidy is, per child, the daily
        # maximum payment (capped at the provider's charge) summed over the days
        # of care, totaled across eligible children, minus the family copayment,
        # floored at zero.
        # We pay every attended day at the per-day rate; the 12-month copay freeze
        # (Section 11(3)(c)) and best-estimate income averaging (Section 8(6)) are
        # not modeled at the moment.
        person = spm_unit.members
        daily_benefit = person("ky_ccap_daily_benefit", period)
        monthly_care_days = person(
            "childcare_attending_days_per_month", period.this_year
        )
        per_child_reimbursement = daily_benefit * monthly_care_days
        total_reimbursement = spm_unit.sum(per_child_reimbursement)
        copay = spm_unit("ky_ccap_copay", period)
        return max_(total_reimbursement - copay, 0)
