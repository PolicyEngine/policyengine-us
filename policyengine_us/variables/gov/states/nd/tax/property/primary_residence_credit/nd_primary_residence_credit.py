from policyengine_us.model_api import *


class nd_primary_residence_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Dakota primary residence credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.tax.nd.gov/prc",
        "https://ndlegis.gov/assembly/69-2025/regular/documents/25-1003-06000.pdf#page=11",
        "https://ndlegis.gov/cencode/t57c02.pdf#page=21",
    )
    defined_for = StateCode.ND

    def formula(tax_unit, period, parameters):
        # The primary residence credit reduces property tax on an
        # owner-occupied primary residence, capped at a flat amount, with no
        # age or income limitation. Renters have no real estate taxes, so the
        # credit is zero for them.
        # N.D.C.C. 57-02-08.9(1)(c)-(d) limits the credit to the property tax
        # due AFTER other chapter 57 credits (e.g. the homestead credit and the
        # disabled veteran credit). Those credits are not modeled, so this caps
        # against gross real_estate_taxes; revisit this base if they are added.
        p = parameters(period).gov.states.nd.tax.property.primary_residence_credit
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        return min_(p.amount, property_tax)
