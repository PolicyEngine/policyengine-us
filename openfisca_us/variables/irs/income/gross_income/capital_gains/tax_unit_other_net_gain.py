from openfisca_us.model_api import *


class tax_unit_other_net_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Other net gain"
    unit = USD
    documentation = "Net gains from property not reported elsewhere."
    definition_period = YEAR

tc_e01200 = taxcalc_read_only_variable("tc_e01200", tax_unit_other_net_gain)