from policyengine_us.model_api import *


class would_file_taxes_voluntarily(Variable):
    value_type = bool
    entity = TaxUnit
    label = "would file taxes voluntarily"
    documentation = """
    Whether this tax unit would file taxes even when not required and not
    seeking a refund from refundable credits. Captures filing for reasons
    such as state requirements, documentation needs, or habit.
    """
    definition_period = YEAR
    default_value = False
