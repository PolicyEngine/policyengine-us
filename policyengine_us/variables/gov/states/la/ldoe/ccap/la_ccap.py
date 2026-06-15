from policyengine_us.model_api import *


class la_ccap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Louisiana Child Care Assistance Program benefit"
    unit = USD
    reference = "https://www.doa.la.gov/media/043btqeh/28v165.docx"
    defined_for = "la_ccap_eligible"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        daily_rate = person("la_ccap_daily_rate", period)
        # Paid day units per child (zero for ineligible children via
        # defined_for on la_ccap_monthly_days).
        monthly_days = person("la_ccap_monthly_days", period)
        # The sliding fee scale co-payment is per child per day; waivers
        # (homelessness, disability, Head Start, STEP) zero it through
        # la_ccap_copay_waived.
        # NOTE: we bill the copay as the daily band x attendance days, per the
        # FFY 2022-2024 CCDF Plan's "copay as a daily rate" framing. The current
        # plan (FFY 2025-2027 Section 3.2.1.b) treats the published monthly band
        # as not varying by hours in care, so this slightly under-charges
        # part-time families; full-time care (the dominant case) is exact.
        unit_copay = spm_unit("la_ccap_daily_copay", period)
        child_copay = spm_unit.project(unit_copay)
        monthly_expense = person("pre_subsidy_childcare_expenses", period)
        capped_charge = min_(monthly_expense, daily_rate * monthly_days)
        per_child = max_(capped_charge - child_copay * monthly_days, 0)
        return spm_unit.sum(per_child)
