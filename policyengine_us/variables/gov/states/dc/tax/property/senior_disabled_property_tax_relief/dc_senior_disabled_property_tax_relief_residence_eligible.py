from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_residence_eligible(Variable):
    """Explicit eligible-property facts for this household's single residence.

    Certifies the District domicile/principal residence, homestead entitlement,
    applicable dwelling-unit and ownership/trust requirements, and no incompatible
    disabled-veterans deduction, for the approved installment coverage entered in
    the pre-relief tax input. It does not certify age, disability, individual
    ownership share or household income. Unknown facts leave this input false,
    suppressing an estimate rather than determining legal ineligibility.
    """

    value_type = bool
    entity = Household
    label = "DC senior disabled property tax relief eligible residence facts"
    definition_period = YEAR
    default_value = False
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-802",
        "https://otr.cfo.dc.gov/page/real-property-tax-reliefs-credits-and-deductions",
    )
