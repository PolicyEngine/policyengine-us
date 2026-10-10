from policyengine_us.model_api import *


class ssi_resource_deeming_excluded_military_resources(Variable):
    value_type = float
    entity = Person
    label = "Unspent retroactive military payments excluded from SSI deeming"
    unit = USD
    definition_period = MONTH
    quantity_type = STOCK
    reference = "https://www.ecfr.gov/current/title-20/section-416.1202"
    documentation = """
    The part of otherwise countable resources consisting of qualifying
    retroactive special pay under 37 USC 310 or combat-zone family separation
    allowance under 37 USC 427. Sections 416.1202(a)(2)-(3) and (b)(1)(ii)-(iii)
    exclude the unspent amount for nine months beginning with the month
    following receipt. Supply only the amount within that exclusion window;
    the model has no payment receipt history from which to derive it.
    """
