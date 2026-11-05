from policyengine_us.model_api import *


class vt_ccfap_family_benefit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = "vt_ccfap_eligible"
    label = "Vermont Child Care Financial Assistance Program benefit to the family"
    documentation = (
        "The part of the provider's charge that CCFAP saves the family. From "
        "December 17, 2023, Vermont pays the provider the state rate less the "
        "family share, even when the provider charges less than the state rate "
        "(vt_ccfap). The family still pays the family share, plus any charge "
        "above the state rate. So the family saves, for each child, the lesser "
        "of the charge and the state rate, less the family share, which is the "
        "amount Vermont paid before that date."
    )
    reference = (
        # Question 1: the family pays the family share to the provider. Question
        # 8: the provider may waive or collect it. Questions 3 and 6 and the
        # "Jane Smith" and "Honey Child Care" examples: the state pays the state
        # rate less the family share, and the family owes any charge above the
        # state rate.
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Understanding-Payments.pdf#page=2",
        # Section 3512(a)(2): the Commissioner sets the family contribution by
        # income and family size and assigns it to the whole family.
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
        # The family's contribution doesn't depend on what providers charge.
        "https://legislature.vermont.gov/assets/Legislative-Reports/Act-76-CCFAP-Rates-Jan-2024.pdf#page=15",
        # Section IV A, Co-Payments, which the June 28, 2024 memo restates: the
        # family pays the provider's fees above the assistance. Vermont wrote
        # this when it paid the lesser of the two rates, so that remainder held
        # the family share.
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=13",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/Act76/Memo-Act-76-CCFAP-Rule-Revision.pdf#page=10",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_child = person("vt_ccfap_eligible_child", period)
        annual_bill = person("pre_subsidy_childcare_expenses", period.this_year)
        # Care hours or a bill stand in for attendance, as in vt_ccfap.
        in_care = (person("childcare_hours_per_week", period.this_year) > 0) | (
            annual_bill > 0
        )
        state_rate = person("vt_ccfap_state_rate", period)
        # With no bill the charge is unknown, so the state rate stands in for
        # it and the family saves what the state pays.
        weekly_charge = where(annual_bill > 0, annual_bill / WEEKS_IN_YEAR, state_rate)
        weekly_saving = min_(state_rate, weekly_charge)
        total_weekly_saving = spm_unit.sum(weekly_saving * eligible_child * in_care)
        monthly_saving = total_weekly_saving * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        family_share = spm_unit("vt_ccfap_family_share", period)
        # A provider may waive the family share. No input records a waiver, so
        # the model assumes the provider collects it. A family whose share exceeds
        # the care CCFAP covers saves nothing: it does better paying the provider's
        # charge itself.
        return max_(monthly_saving - family_share, 0)
