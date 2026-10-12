from policyengine_us.model_api import *


class nc_sa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina Special Assistance eligibility"
    definition_period = MONTH
    defined_for = StateCode.NC
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-Manual-Rev-June-2026.pdf",
        "https://policies.ncdhhs.gov/wp-content/uploads/Special-Assistance-In-Home-Program-Manual-Rev-June-2026.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.dhhs.sa
        setting = person("nc_sa_care_setting", period)
        settings = setting.possible_values
        age = person("age", period.this_year)
        in_home = (setting == settings.IN_HOME) | (setting == settings.IN_HOME_ENHANCED)
        adult = age >= p.minimum_adult_age
        age_eligible = adult | (person("is_blind", period.this_year) & ~in_home)
        receives_ssi = person("ssi", period) > 0
        # SSI receipt establishes the resource test. Non-SSI cases use an
        # individual state budget, in addition to SSI non-income eligibility.
        resource_limit = parameters(
            period
        ).gov.ssa.ssi.eligibility.resources.limit.individual
        resources = person("ssi_countable_resources", period.this_year)
        resources_eligible = receives_ssi | (resources <= resource_limit)
        ssi_status = receives_ssi | person("is_ssi_eligible", period)
        enhanced = (setting == settings.SPECIAL_CARE_UNIT) | (
            setting == settings.IN_HOME_ENHANCED
        )
        income_limit = where(enhanced, p.income_limit.enhanced, p.income_limit.basic)
        # The monthly income test still applies when the first payment is
        # prorated without subtracting income (SA-3220 II.E and III).
        countable_income = person("nc_sa_countable_income", period)
        # Annual-to-month arithmetic can put an exact cutoff one storage
        # step below it. Preserve sub-cent income; do not round the budget.
        comparison_limit = np.nextafter(
            income_limit.astype(countable_income.dtype),
            -np.inf,
            dtype=countable_income.dtype,
        )
        income_eligible = countable_income < comparison_limit
        return (
            (setting != settings.NONE)
            & age_eligible
            & resources_eligible
            & ssi_status
            & income_eligible
            & person("takes_up_ssi_if_eligible", period.this_year)
        )
