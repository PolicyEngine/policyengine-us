from policyengine_core.reforms import Reform


class taxsim(Reform):
    def apply(self):
        self.modify_parameters(modify_parameters)


def modify_parameters(parameters):
    parameters.contrib.nber.taxsim35_emulation.update(
        start="2019-01-01", value=True
    )
    return parameters
