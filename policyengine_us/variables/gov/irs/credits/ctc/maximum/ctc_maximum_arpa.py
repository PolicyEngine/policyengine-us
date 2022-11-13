from policyengine_us.model_api import *


class ctc_maximum_arpa(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC for ARPA"
    unit = USD
    documentation = "Maximum value of the Child Tax Credit, before phase-out."
    definition_period = YEAR

    formula = sum_of_variables(["ctc_individual_maximum"])
