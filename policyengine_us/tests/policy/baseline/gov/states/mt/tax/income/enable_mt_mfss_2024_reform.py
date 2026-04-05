from policyengine_core.model_api import *
from policyengine_core.periods import instant


def modify_parameters(parameters):
    parameters.gov.states.mt.tax.income.married_filing_separately_on_same_return_allowed.update(
        start=instant("2024-01-01"), stop=instant("2024-12-31"), value=True
    )
    return parameters


class enable_mt_mfss_2024_reform(Reform):
    def apply(self):
        self.modify_parameters(modify_parameters)
