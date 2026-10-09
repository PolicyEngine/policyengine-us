from policyengine_us.model_api import *


class capped_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Local real estate taxes limited by the federal SALT cap."
    unit = USD
    documentation = (
        "The head's and spouse's real estate taxes, limited by the federal "
        "SALT cap. A dependent's own real estate taxes belong on the "
        "dependent's return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/26/1.164-1",
        "https://www.law.cornell.edu/uscode/text/26/164",
    )

    def formula(tax_unit, period, parameters):
        # Taxes are deductible only by the person on whom they are imposed
        # (26 CFR 1.164-1(a)), so leave dependents' own taxes out.
        property_taxes = tax_unit_non_dep_add(tax_unit, period, ["real_estate_taxes"])
        p = parameters(period).gov.irs.deductions.itemized
        cap = p.salt_and_real_estate.cap[tax_unit("filing_status", period)]
        return min_(property_taxes, cap)
