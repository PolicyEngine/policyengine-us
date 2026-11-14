from policyengine_us.model_api import *


class WIVeteransPropertyTaxCreditClaimantType(Enum):
    ELIGIBLE_VETERAN = "WDVA verified eligible veteran"
    UNREMARRIED_SURVIVOR = "WDVA verified eligible unremarried surviving spouse"
    ELIGIBLE_SPOUSE_SEPARATE_RETURN = "Eligible veteran's spouse on a separate return"
    NOT_ELIGIBLE = "Known not to meet a statutory claimant category"
    UNKNOWN = "Claimant category is unknown"


class wi_veterans_property_tax_credit_claimant_type(Variable):
    """Source-verified statutory claimant route, distinct from generic statuses.

    The spouse route requires the linked eligible veteran and separate-return
    facts; a generic filing-status, disability or survivor flag is insufficient.
    """

    value_type = Enum
    entity = TaxUnit
    label = "Wisconsin veterans property tax credit claimant type"
    definition_period = YEAR
    possible_values = WIVeteransPropertyTaxCreditClaimantType
    default_value = WIVeteransPropertyTaxCreditClaimantType.UNKNOWN
    reference = "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/6e"
