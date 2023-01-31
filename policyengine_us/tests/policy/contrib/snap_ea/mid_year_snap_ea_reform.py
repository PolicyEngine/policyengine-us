from policyengine_core.model_api import *
from policyengine_core.periods import instant


def modify_parameters(parameters):
    parameters.gov.usda.snap.emergency_allotment.in_effect.CA.update(
        start=instant("2022-04-08"), stop=instant("2027-12-31"), value=0
    )
    return parameters


class abolish_ca_snap_ea_may_22(Reform):
    def apply(self):
        self.modify_parameters(modify_parameters)
