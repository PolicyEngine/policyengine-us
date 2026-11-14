from policyengine_us.model_api import *


class wv_sctc_qualified_property_taxes_paid(Variable):
    """Whole cohort's principal paid in the income year, after discounts, before SCTC.

    Include regular, excess and bond levies; exclude penalties and interest.
    This is not the tax already allocated to the capped assessed-value slice.
    """

    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    default_value = -1
    label = "West Virginia SCTC full qualifying property taxes paid"
    reference = "https://code.wvlegislature.gov/11-21-21/"
    defined_for = StateCode.WV
