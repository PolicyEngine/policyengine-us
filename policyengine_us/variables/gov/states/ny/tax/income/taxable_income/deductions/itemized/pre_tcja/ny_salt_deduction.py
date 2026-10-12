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
    - State and local income taxes are NOT deductible (add-back required per § 615(c)(1))
    - State and local general sales taxes are NOT deductible (add-back required per § 615(c)(1))
    - Real estate taxes ARE deductible
    """

    def formula(tax_unit, period, parameters):
        # NY Tax Law § 615(c)(1): state and local general sales taxes are added
        # back (like income taxes). Only real estate taxes remain deductible.
        return add(tax_unit, period, ["real_estate_taxes"])
