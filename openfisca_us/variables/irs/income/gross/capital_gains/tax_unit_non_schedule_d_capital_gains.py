from openfisca_us.model_api import *


class tax_unit_non_schedule_d_capital_gains(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capital gains not reported on Schedule D"
    unit = USD
    definition_period = YEAR

tc_e01100 = taxcalc_read_only_variable("tc_e01100", tax_unit_non_schedule_d_capital_gains)