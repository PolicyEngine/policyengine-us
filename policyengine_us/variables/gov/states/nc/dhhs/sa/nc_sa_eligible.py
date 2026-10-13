from policyengine_us.model_api import *


class nc_sa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina Special Assistance eligibility"
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = (
        # PDF pages 6-7, 61, 207, 209
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf#page=6",
        # PDF pages 14, 18, 41
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf#page=14",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.dhhs.sa
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        age = person("age", period.this_year)
        in_home = (setting == settings.IN_HOME) | (setting == settings.IN_HOME_ENHANCED)
        adult = age >= p.minimum_adult_age
        age_eligible = adult | (person("is_blind", period.this_year) & ~in_home)
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # An SSI recipient automatically meets the categorical, financial and
        # resource requirements (SA-3100 II.B; SA-3200 I.A). A non-SSI
        # applicant must meet SSI's non-income requirements, but SA tests only
        # the applicant's own resources: "The budget unit is always one"
        # (SA-3200 I), so SSI's couple and spousal resource rules do not apply.
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period.this_year)
        immigration_status = person("immigration_status", period.this_year)
        citizen = immigration_status == immigration_status.possible_values.CITIZEN
        immigration_eligible = citizen | person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        resource_limit = parameters(
            period
        ).gov.ssa.ssi.eligibility.resources.limit.individual
        resources = person("ssi_countable_resources", period.this_year)
        non_ssi_eligible = (
            aged_blind_disabled & immigration_eligible & (resources <= resource_limit)
        )
        enhanced = (setting == settings.SPECIAL_CARE_UNIT) | (
            setting == settings.IN_HOME_ENHANCED
        )
        income_limit = where(enhanced, p.income_limit.enhanced, p.income_limit.basic)
        # The monthly income test still applies when the first payment is
        # prorated without subtracting income (SA-3220 II.E and IV.A).
        countable_income = person("nc_sa_countable_income", period)
        # TCMI and the cutoff are amounts in cents (ineligible at $1,466.51 or
        # more), so compare whole cents rather than the float values that
        # annual-to-month arithmetic produces.
        income_cents = np.floor(countable_income.astype(np.float64) * 100 + 0.5)
        limit_cents = np.floor(income_limit * 100 + 0.5)
        return (
            (setting != settings.NONE)
            & age_eligible
            & (receives_ssi | non_ssi_eligible)
            & (income_cents < limit_cents)
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
