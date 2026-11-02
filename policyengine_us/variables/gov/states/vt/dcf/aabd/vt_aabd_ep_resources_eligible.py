from policyengine_us.model_api import *


class vt_aabd_ep_resources_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Vermont Essential Person resource eligibility"
    definition_period = MONTH
    # PDF pages 42, 46-47
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=42"
    documentation = "SSI/AABD receipt by a member of the assistance group living in the same household automatically passes the resource test; otherwise the group passes through vt_aabd_ep_passes_state_resource_test."

    def formula(person, period, parameters):
        receives = (
            (person("ssi", period) > 0)
            | person("receives_ssi", period)
            | (person("vt_aabd_federal", period) > 0)
        )
        passes_state_test = person("vt_aabd_ep_passes_state_resource_test", period)
        arrangement = person("vt_aabd_living_arrangement", period)
        la = arrangement.possible_values
        # Rule 2782: the group includes only members living in the same
        # household, so a spouse in a facility cannot pass the test for the
        # spouse at home.
        in_household = (arrangement == la.INDEPENDENT) | (
            arrangement == la.HOUSEHOLD_OF_ANOTHER
        )
        # Rule 2785 tests the assistance group's combined resources once.
        return person.marital_unit.any((receives | passes_state_test) & in_household)
