from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.tax_unit.filing_status import (
    FilingStatus,
)


class clean_vehicle_credit_prior_year_filing_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = FilingStatus
    default_value = FilingStatus.SINGLE
    definition_period = YEAR
    label = "Filing status for the year before a clean vehicle purchase"
    documentation = (
        "Filing status on the preceding year's return (Form 8936 line 5). "
        "The preceding year's modified AGI is compared with the income limit "
        "for this filing status. When not provided, it defaults to the "
        "current year's filing status."
    )
    reference = (
        # Special rule for change in filing status.
        "https://www.ecfr.gov/current/title-26/part-1/section-1.30D-4#p-1.30D-4(b)(3)",
        "https://www.ecfr.gov/current/title-26/part-1/section-1.25E-1#p-1.25E-1(c)(3)",
        "https://www.irs.gov/pub/irs-prior/f8936--2024.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit("filing_status", period)
