from policyengine_us.model_api import *


class sd_ssp_care(Variable):
    value_type = float
    entity = Person
    label = "South Dakota optional supplemental care payment"
    definition_period = MONTH
    unit = USD
    reference = "https://sdlegislature.gov/Rules/Administrative/67:46:06"
    defined_for = StateCode.SD

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sd.dss.ssp
        resources = person("ssi_countable_resources", period.this_year)
        joint_entry = person("sd_ssp_care_joint_entry", period)
        resources = where(joint_entry, person.marital_unit.sum(resources), resources)
        limit = where(joint_entry, p.joint_entry_resource_limit, p.resource_limit)
        immigration = person("immigration_status", period.this_year)
        citizenship = (immigration == immigration.possible_values.CITIZEN) | person(
            "is_ssi_qualified_noncitizen", period.this_year
        )
        eligible = (
            person("sd_ssp_care_certified", period)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & citizenship
            & (resources <= limit)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period)
        )
        days = clip(person("sd_ssp_care_days", period), 0, period.days)
        cost = max_(person("sd_ssp_approved_care_cost", period), 0)
        foster = person("sd_ssp_is_adult_foster_care", period)
        cost = where(foster, cost, min_(cost, days * p.assisted_living_daily_rate))
        # Care uses gross income, including SSI, before state-approved
        # deductions. Federal SSI's $20/$65 exclusions are not applied.
        income = (
            max_(person("ssi_earned_income", period), 0)
            + max_(person("ssi_unearned_income", period), 0)
            + person("ssi", period)
        )
        contribution = max_(income - person("sd_ssp_care_income_deductions", period), 0)
        contribution = where(
            person("sd_ssp_care_income_not_applied", period), 0, contribution
        )
        return eligible * (days > 0) * max_(cost - contribution, 0)
