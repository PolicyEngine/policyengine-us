from policyengine_us.model_api import *


class is_snap_prorated_income_member(Variable):
    value_type = bool
    entity = Person
    label = "SNAP ineligible member with prorated income"
    definition_period = MONTH
    documentation = (
        "Whether this person's income is prorated under 7 CFR "
        "273.11(c)(2): ineligible aliens without a state full-count "
        "election and ABAWD time-limit ineligible members (273.24). "
        "Members failing the general work requirements fall under "
        "273.11(c)(1), which counts their income in full. The model "
        "treats modeled noncompliance as a state-imposed disqualification, "
        "consistent with these members' exclusion from the SNAP unit size."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2_ii",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.income.ineligible_members
        immigration_ineligible = ~person("is_snap_immigration_status_eligible", period)
        state = person.household("state_code_str", period)
        discretion_alien = person("is_snap_state_discretion_ineligible_alien", period)
        counts_all = np.isin(state, p.count_all_income_states)
        full_count_alien = discretion_alien & counts_all
        student = person("is_snap_ineligible_student", period.this_year)
        prorated_alien = immigration_ineligible & ~student & ~full_count_alien
        # ABAWD time-limit ineligible members are prorated under
        # 273.11(c)(2); members sanctioned for noncompliance with the
        # general work requirements fall under 273.11(c)(1), which counts
        # their income and expenses in full. In count-all states the
        # state's full-count election for the alien's income governs.
        fails_abawd_time_limit = person(
            "meets_snap_general_work_requirements", period
        ) & ~person("meets_snap_work_requirements_person", period)
        return prorated_alien | (fails_abawd_time_limit & ~student & ~full_count_alien)
