from policyengine_us.model_api import *


class eitc_legal_separation_and_apart_at_year_end(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer has a qualifying separation instrument and separate household at year end"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#d_2_B_iii_II",
        "https://www.law.cornell.edu/uscode/text/26/121#d_3_C",
    )
    documentation = """
    Whether the filer has a decree of separate maintenance, written
    separation agreement, or other qualifying instrument under IRC
    121(d)(3)(C), other than a decree of divorce, and is not a member of
    the spouse's household at the end of the tax year. Both conditions
    must hold. Defaults to false when these facts are not supplied.
    """
