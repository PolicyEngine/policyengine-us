from policyengine_us.model_api import *


class id_salt_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho SALT deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        state_and_local_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # If the salt amount is above the federal cap, Idaho applies separate limitations
        filing_status = tax_unit("filing_status", period)
        cap = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.cap[filing_status]
        # Federal Schedule A line 5b - State and local real estate taxes
        # Federal Schedule A line 5c - State and local personal property taxes
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        salt_and_real_estate_tax = state_and_local_tax + real_estate_taxes
        salt_above_cap = salt_and_real_estate_tax > cap
        reduced_cap = max_(cap - real_estate_taxes, 0)
        return where(salt_above_cap, reduced_cap, state_and_local_tax)
