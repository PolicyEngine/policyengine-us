from policyengine_us.model_api import *


class ct_income_tax_before_personal_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax before personal tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    adds = [
        "ct_income_tax_main_rates",
        "ct_income_tax_phase_out_add_back",
        "ct_income_tax_recapture",
    ]
