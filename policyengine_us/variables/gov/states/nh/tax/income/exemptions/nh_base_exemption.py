from policyengine_us.model_api import *


class nh_base_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire base exemption household level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    adds = "gov.states.nh.tax.income.exemptions.amount.base"