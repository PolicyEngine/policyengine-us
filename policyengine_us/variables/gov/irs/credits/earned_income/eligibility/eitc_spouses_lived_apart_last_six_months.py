from policyengine_us.model_api import *


class eitc_spouses_lived_apart_last_six_months(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Spouses had different principal residences for the last six months"
    definition_period = YEAR
    default_value = False
    reference = "https://www.law.cornell.edu/uscode/text/26/32#d_2_B_iii_I"
    documentation = """
    Whether the filer and spouse had different principal places of abode
    throughout the last six months of the tax year. A current separation
    indicator alone does not establish this condition. Defaults to false
    when this separation fact is not supplied.
    """
