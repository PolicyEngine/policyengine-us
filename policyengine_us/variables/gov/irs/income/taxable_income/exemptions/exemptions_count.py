from policyengine_us.model_api import *


class exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of tax exemptions"
    unit = USD
    definition_period = YEAR

    adds = ["tax_unit_size"]
