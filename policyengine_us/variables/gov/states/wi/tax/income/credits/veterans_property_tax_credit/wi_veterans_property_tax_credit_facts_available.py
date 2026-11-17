from policyengine_us.model_api import *


class wi_veterans_property_tax_credit_facts_available(Variable):
    """Nonmonetary facts for this return's active claim are traceably known.

    Covers claimant, WDVA effective periods, property/allocation basis, claim
    permission, this-return election, actual incompatible claims and the valid
    actual retirement-exclusion claim fact, including verified negative facts.
    Does not require a known monetary total or subsume
    the separate counterpart-spouse claim-status input. Unresolved acreage or
    midyear certification source conflicts remain unavailable. False defaults
    do not establish legal ineligibility or a zero entitlement.
    """

    value_type = bool
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit legal facts are known"
    definition_period = YEAR
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e"
