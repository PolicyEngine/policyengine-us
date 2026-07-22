from policyengine_us.model_api import *


class is_snap_gross_test_full_income_count_alien(Variable):
    value_type = bool
    entity = Person
    label = (
        "SNAP ineligible alien with fully counted income under the gross income test"
    )
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/7/273.11#c_3_i"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.snap.income.ineligible_members
        state = person.household("state_code_str", period)
        discretion_alien = person("is_snap_state_discretion_ineligible_alien", period)
        hybrid_state = np.isin(state, p.gross_test_full_count_states)
        return discretion_alien & hybrid_state
