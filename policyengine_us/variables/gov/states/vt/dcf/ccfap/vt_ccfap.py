from policyengine_us.model_api import *


class vt_ccfap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible"
    label = "Vermont Child Care Financial Assistance Program benefit"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=13",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=17",
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
    )

    def formula(spm_unit, period, parameters):
        # From 2023-12-17 payment is based on the state rate regardless of the
        # provider's charges. Before then, Vermont paid the lesser of the state
        # rate and the provider's rate, and the family's bill stands in for that.
        # With no bill the charge is unknown, so nothing caps the state rate. The
        # model reads parameters at the start of each month, so all of December
        # 2023 falls under the earlier rule.
        # Source: CCFAP Understanding Payments (Q3 and "Jane Smith" example)
        # https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf
        # CCFAP Regulations V pays from the first day of eligibility and actual
        # attendance, so a child who attends no provider draws nothing. Care hours
        # or a bill stand in for attendance.
        p = parameters(period).gov.states.vt.dcf.ccfap.rates
        person = spm_unit.members
        eligible_child = person("vt_ccfap_eligible_child", period)
        annual_bill = person("pre_subsidy_childcare_expenses", period.this_year)
        in_care = (person("childcare_hours_per_week", period.this_year) > 0) | (
            annual_bill > 0
        )
        state_rate = person("vt_ccfap_state_rate", period)
        weekly_rate = where(
            p.pays_above_provider_charge | (annual_bill == 0),
            state_rate,
            min_(state_rate, annual_bill / WEEKS_IN_YEAR),
        )
        total_weekly_rate = spm_unit.sum(weekly_rate * eligible_child * in_care)
        monthly_rate = total_weekly_rate * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        family_share = spm_unit("vt_ccfap_family_share", period)
        return max_(monthly_rate - family_share, 0)
