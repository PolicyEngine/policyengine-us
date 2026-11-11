from policyengine_us.model_api import *


class sd_cca(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Dakota Child Care Assistance benefit amount"
    definition_period = MONTH
    defined_for = "sd_cca_eligible"
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:15",
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:16",
        # PDF pages 18-24.
        "https://web.archive.org/web/20251031171652/https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=18",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.cca.rates
        person = spm_unit.members
        is_eligible_child = person("sd_cca_eligible_child", period)
        if p.uses_weekly_rates:
            # The weekly schedule starts at one hour of care per week.
            in_care = person("childcare_hours_per_week", period.this_year) > 0
            weekly_rate = person("sd_cca_weekly_rate", period)
            weekly_to_monthly = WEEKS_IN_YEAR / MONTHS_IN_YEAR
            max_reimbursement = (
                spm_unit.sum(weekly_rate * is_eligible_child * in_care)
                * weekly_to_monthly
            )
        else:
            if not p.hourly.available:
                return 0
            hourly_rate = person("sd_cca_hourly_rate", period)
            # Care hours stand in for DSS-authorized weekly need. Section 8
            # converts weekly need with 4.3; rounding up matches its example
            # of 45 weekly hours becoming 194 monthly hours. DSS imposes no
            # general monthly cap on ordinary CCA authorized hours.
            hours = max_(person("childcare_hours_per_week", period.this_year), 0)
            monthly_hours = np.ceil(hours * p.hourly.weeks_per_month)
            max_reimbursement = spm_unit.sum(
                hourly_rate * monthly_hours * is_eligible_child
            )
        # Family expenses pool the per-child ceilings. Both eras subtract the
        # co-payment after applying the billed-expense ceiling.
        actual_expenses = spm_unit("spm_unit_pre_subsidy_childcare_expenses", period)
        capped_expenses = min_(actual_expenses, max_reimbursement)
        copay = spm_unit("sd_cca_copay", period)
        return max_(capped_expenses - copay, 0)
