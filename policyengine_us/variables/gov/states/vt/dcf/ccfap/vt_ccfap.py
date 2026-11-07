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
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=11",
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
        # Under CCFAP Regulations V, as the department revised it on June 28,
        # 2024, payment runs from the first week of submitted attendance, so a
        # child who attends no provider draws nothing. With no attendance
        # record, care hours stand in for attendance. When no one in the SPM
        # unit has care hours, a share of the unit's bill stands in instead;
        # pre_subsidy_childcare_expenses splits that bill evenly across the
        # unit's children.
        p = parameters(period).gov.states.vt.dcf.ccfap.rates
        person = spm_unit.members
        eligible_child = person("vt_ccfap_eligible_child", period)
        annual_bill = person("pre_subsidy_childcare_expenses", period.this_year)
        has_hours = person("childcare_hours_per_week", period.this_year) > 0
        unit_has_hours = spm_unit.project(spm_unit.any(has_hours))
        in_care = where(unit_has_hours, has_hours, annual_bill > 0)
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
