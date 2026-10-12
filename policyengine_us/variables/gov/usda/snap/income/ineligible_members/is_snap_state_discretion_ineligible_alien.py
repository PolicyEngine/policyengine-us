from policyengine_us.model_api import *


class is_snap_state_discretion_ineligible_alien(Variable):
    value_type = bool
    entity = Person
    label = "SNAP ineligible alien whose income treatment is at state discretion"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.income.ineligible_members
        immigration_ineligible = ~person("is_snap_immigration_status_eligible", period)
        status = person("immigration_status", period.this_year).decode_to_str()
        state_discretion_status = np.isin(status, p.pre_prwora_statuses)
        # Ineligible students are treated as nonhousehold members under
        # 273.11(d) rather than under the ineligible-alien rules.
        student = person("is_snap_ineligible_student", period.this_year)
        return ~student & immigration_ineligible & state_discretion_status
