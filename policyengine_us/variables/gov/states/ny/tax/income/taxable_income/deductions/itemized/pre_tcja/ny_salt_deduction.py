from policyengine_us.model_api import *


class ny_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY SALT deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions.htm",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. For SALT:
    - No $10,000 cap applies
    - State and local income taxes are NOT deductible (add-back required per § 615(c))
    - State and local sales taxes ARE deductible
    - Real estate taxes ARE deductible
    """

    def formula(tax_unit, period, parameters):
        # NY allows sales tax and real estate taxes, but NOT income taxes
        # Per Tax Law § 615(c), state/local income taxes must be subtracted
        sales_tax = add(
            tax_unit, period, ["state_sales_tax", "local_sales_tax"]
        )
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        return sales_tax + real_estate_taxes
