from policyengine_us.model_api import *


class state_property_tax_refunds(Variable):
    value_type = float
    entity = TaxUnit
    label = "State property tax and rent refunds paid outside the income tax"
    documentation = (
        "Property tax and rent refunds that states pay in cash on their own "
        "claims, outside the income tax return. household_state_benefits and "
        "spm_unit_benefits both count them."
    )
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_property_tax_refunds"
