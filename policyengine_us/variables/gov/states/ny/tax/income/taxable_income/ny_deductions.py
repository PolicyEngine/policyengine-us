from policyengine_us.model_api import *


class ny_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY income deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/613",
        "https://www.tax.ny.gov/pdf/2017/inc/it201i_2017.pdf#page=20",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        # ny_itemizes makes the election. Before 2018 only a federal itemizer
        # may itemize (N.Y. Tax Law 615(a)). A filer with college tuition
        # expenses itemizes when that lowers New York State plus City tax, and
        # any other filer when the itemized deduction exceeds the standard
        # deduction.
        return where(
            tax_unit("ny_itemizes", period),
            tax_unit("ny_itemized_deductions", period),
            tax_unit("ny_standard_deduction", period),
        )
