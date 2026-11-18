from policyengine_us.model_api import *


class ut_heat_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Meets the Utah HEAT citizenship or immigration requirement"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/200_Program_Standards/203_Citizenship_and_Non-Citizenship_Requirements/203-2B_Qualified_and_Eligible_Non-Citizens.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ut.dwf.heat.eligibility.immigration
        status = person("immigration_status", period).decode_to_str()
        eligible_status = np.isin(status, p.eligible_statuses)
        conditional_status = np.isin(status, p.conditional_statuses)
        waited = person("years_since_us_entry", period) >= p.waiting_period
        served = person("is_veteran", period) | person("is_military", period)
        # Marital units identify spouses; tax-unit roles and the child link
        # identify dependent children. Unrelated household members do not confer
        # the exception. Supply these units/links explicitly for complex families.
        self_or_spouse_served = person.marital_unit.any(served)
        dependent_child = person("is_tax_unit_dependent", period) & person(
            "is_child_of_tax_head", period
        )
        parent_served = person.tax_unit.any(
            served & person("is_tax_unit_head_or_spouse", period)
        )
        military_connection = self_or_spouse_served | (dependent_child & parent_served)
        # The existing service flags do not distinguish honorable discharge or
        # full-time active duty from National Guard service. The entry clock
        # stands for years in qualified status, not merely physical presence.
        # COFA, trafficking, battered and special Afghan/Ukrainian statuses are
        # not separately observable. LPR is expressly eligible in section 203-2B;
        # SNAP's broader waiting-period and child-age rules are not imported.
        return eligible_status | (conditional_status & (waited | military_connection))
