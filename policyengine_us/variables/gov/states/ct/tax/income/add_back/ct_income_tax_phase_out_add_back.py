from policyengine_us.model_api import *


class ct_income_tax_phase_out_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax phase out add back"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):