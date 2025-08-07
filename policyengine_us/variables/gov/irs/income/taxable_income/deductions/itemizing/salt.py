from policyengine_us.model_api import *


class salt(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "State and local sales or income tax and real estate taxes subject to the SALT deduction"
    unit = USD

    adds = "gov.irs.deductions.itemized.salt_and_real_estate.sources"
