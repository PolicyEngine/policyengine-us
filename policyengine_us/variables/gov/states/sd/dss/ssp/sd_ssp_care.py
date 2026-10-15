from policyengine_us.model_api import *


class sd_ssp_care(Variable):
    value_type = float
    entity = Person
    label = "South Dakota optional supplemental care payment"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://sdlegislature.gov/Rules/Administrative/67:46:04:10",
        "https://sdlegislature.gov/Rules/Administrative/67:46:04:13",
        "https://sdlegislature.gov/Rules/Administrative/67:46:04:15",
        "https://sdlegislature.gov/Rules/Administrative/67:46:05:30",
        "https://sdlegislature.gov/Rules/Administrative/67:46:06:03",
        "https://sdlegislature.gov/Rules/Administrative/67:46:06:09",
        "https://sdlegislature.gov/Rules/Administrative/67:46:06:10",
        "https://sdlegislature.gov/Rules/Administrative/67:46:01:14",
    )
    defined_for = StateCode.SD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.ssp
        resources = person("ssi_countable_resources", period.this_year)
        # Joint entry applies only when both spouses are flagged.
        joint_entry = (
            person.marital_unit.sum(person("sd_ssp_care_joint_entry", period)) > 1
        )
        resources = where(joint_entry, person.marital_unit.sum(resources), resources)
        limit = where(joint_entry, p.joint_entry_resource_limit, p.resource_limit)
        immigration = person("immigration_status", period.this_year)
        citizenship = (immigration == immigration.possible_values.CITIZEN) | person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        # ARSD 67:46:04:13(2) refers a resident whose income would qualify for
        # SSI to apply, and 67:46:01:14 disqualifies one who fails to take
        # advantage of it; a resident over income for SSI need not apply.
        pursues_ssi = person("takes_up_ssi_if_eligible", period.this_year) | (
            person("uncapped_ssi", period) <= 0
        )
        eligible = (
            person("sd_ssp_care_certified", period)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & citizenship
            & (resources <= limit)
            & ~person("is_incarcerated", period)
            & pursues_ssi
        )
        partial_days = person("sd_ssp_care_partial_month_days", period)
        partial_month = (partial_days > 0) & (partial_days < period.days)
        days = where(partial_month, partial_days, period.days)
        cost = max_(person("sd_ssp_approved_care_cost", period), 0)
        setting = person("sd_ssp_care_setting", period)
        foster = setting == setting.possible_values.ADULT_FOSTER_CARE
        cost = where(foster, cost, min_(cost, days * p.assisted_living_daily_rate))
        # ARSD 67:46:04:15 makes a resident whose net income exceeds the monthly
        # care rate ineligible. 67:46:06:01 applies this chapter 67:46:04 test
        # before the 67:46:06:09 partial-month rule, so the covered-days charge
        # is scaled to a full month.
        monthly_rate = cost * period.days / days
        # Care uses gross income, including SSI, before state-approved
        # deductions. Federal SSI's $20/$65 exclusions are not applied.
        own_income = (
            max_(person("ssi_earned_income", period), 0)
            + max_(person("ssi_unearned_income", period), 0)
            + person("ssi", period)
        )
        # ARSD 67:46:04:10(6), applied to the payment by 67:46:06:03: when both
        # spouses enter care in the same month, their combined income is shared
        # equally in that month. The share is taken before each spouse's own
        # deductions (67:46:06:05 to 06:07), following the order of the rules.
        # NOTE: the month only one spouse of a couple living together enters
        # assisted living or adult foster care is not modeled. 67:46:04:10(7)
        # and 67:46:05:42(7) count the couple's combined income and resources
        # in that month; this formula uses the entering spouse's own.
        shared_income = person.marital_unit.sum(own_income) / (
            person.marital_unit.nb_persons()
        )
        income = where(joint_entry, shared_income, own_income)
        net_income = max_(income - person("sd_ssp_care_income_deductions", period), 0)
        # 67:46:06:09: income is not applied in a partial month unless the
        # recipient died or transferred to another long-term care facility.
        income_not_applied = partial_month & ~person(
            "sd_ssp_care_died_or_transferred", period
        )
        contribution = where(income_not_applied, 0, net_income)
        return eligible * (net_income <= monthly_rate) * max_(cost - contribution, 0)
