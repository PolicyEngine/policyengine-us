from policyengine_us.model_api import *


class az_families_tax_rebate_received(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate received"
    unit = USD
    documentation = (
        "Amount of Arizona Families Tax Rebate received that was included "
        "in federal adjusted gross income."
    )
    definition_period = YEAR
