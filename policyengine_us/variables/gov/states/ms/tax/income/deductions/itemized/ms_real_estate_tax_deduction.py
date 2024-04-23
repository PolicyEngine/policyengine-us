from policyengine_us.model_api import *


class ms_real_estate_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi real estate tax deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=15"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # State income taxes paid or any other taxes
        # allowed in lieu of federal purposes including
        # withholding taxes on Mississippi gaming
        # winnings, are not deductible as an itemized deduction.
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        filing_status = tax_unit("filing_status", period)
        return min_(real_estate_taxes, p.cap[filing_status])
