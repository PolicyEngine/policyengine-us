from policyengine_us.model_api import *


class ga_caps_provider_published_rate(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "Georgia CAPS provider published weekly rate per child"
    defined_for = "ga_caps_eligible_child"
    reference = "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=55"

    def formula(person, period, parameters):
        spm_unit = person.spm_unit
        annual_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period.this_year
        )
        num_eligible = add(spm_unit, period, ["ga_caps_eligible_child"])
        weekly_per_child = where(
            num_eligible > 0,
            annual_expenses / num_eligible / WEEKS_IN_YEAR,
            0,
        )
        return spm_unit.project(weekly_per_child)
