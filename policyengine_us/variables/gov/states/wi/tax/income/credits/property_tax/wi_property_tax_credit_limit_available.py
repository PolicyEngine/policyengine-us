from policyengine_us.model_api import *


class wi_property_tax_credit_limit_available(Variable):
    """Whether the filing facts determine the School Property Credit ceiling.

    This does not certify the credit's other eligibility or expense facts.
    An unknown head-of-household marital status leaves the legacy potential
    amount available for compatibility, without validating its ceiling.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin school property tax credit ceiling facts are known"
    definition_period = YEAR
    defined_for = StateCode.WI
    reference = (
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1-Inst.pdf#page=18",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/9/b",
    )

    def formula_2025_01_01(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        head_of_household = (
            filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD
        )
        marital_status = tax_unit(
            "wi_school_property_tax_credit_marital_status", period
        )
        marital_status_known = marital_status != marital_status.possible_values.UNKNOWN
        return ~head_of_household | marital_status_known
