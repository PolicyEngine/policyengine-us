from policyengine_us.model_api import *


class ny_real_property_tax_credit_property_market_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York real property tax credit total property market value"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    default_value = 0
    documentation = (
        "Current full market value of all distinct real properties owned by the "
        "claimant and, for a joint claim, their spouse, including residences, "
        "rental property, garages, and land. Include the full property values "
        "before ownership-share proration or debt deductions. Callers must "
        "supply this total for an audited IT-214 eligibility result; an "
        "unspecified value is not a verified zero. Claimants who own no real "
        "property may explicitly enter zero. Assessed values and primary-home "
        "values alone do not establish this total."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (e)(7)
        "https://www.tax.ny.gov/pdf/2025/inc/it214i_2025.pdf#page=1",
    )
