from policyengine_us.model_api import *


class WISchoolPropertyTaxCreditMaritalStatus(Enum):
    MARRIED = "Legally married for the Wisconsin return"
    UNMARRIED = "Legally unmarried for the Wisconsin return"
    UNKNOWN = "Legal marital status for the Wisconsin return is unknown"


class wi_school_property_tax_credit_marital_status(Variable):
    """Actual source-return marital status for the head-of-household ceiling.

    Wisconsin distinguishes married and unmarried head-of-household filers.
    Family membership or separation from a partner does not establish this
    legal status. The unknown default is not a statement that the filer is
    unmarried; the separate limit-availability output reports that uncertainty.
    """

    value_type = Enum
    entity = TaxUnit
    label = "Wisconsin school property tax credit legal marital status"
    definition_period = YEAR
    possible_values = WISchoolPropertyTaxCreditMaritalStatus
    default_value = WISchoolPropertyTaxCreditMaritalStatus.UNKNOWN
    reference = (
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=18",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/9/b",
    )
