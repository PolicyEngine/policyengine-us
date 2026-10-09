from policyengine_us.model_api import *


class salt(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "State and local sales or income tax and real estate taxes subject to the SALT deduction"
    unit = USD
    documentation = (
        "State and local taxes the head and spouse can deduct before the SALT "
        "cap. A dependent's own real estate taxes belong on the dependent's "
        "return."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/164",
        "https://www.law.cornell.edu/cfr/text/26/1.164-1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        # Taxes are deductible only by the person on whom they are imposed
        # (26 CFR 1.164-1(a)). Tax-unit sources are added as they are.
        return tax_unit_non_dep_add(tax_unit, period, p.sources)
