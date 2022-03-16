from openfisca_us.model_api import *


class c21040(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Phased-out itemized deductions"
    unit = USD
    documentation = "Itemized deductions that are phased out"

    def formula(tax_unit, period, parameters):
        nonlimited = add(tax_unit, period, ["c17000", "c20500"])
        phaseout = parameters(period).irs.deductions.itemized.phaseout
        mars = tax_unit("mars", period)
        c21060 = tax_unit("c21060", period)
        phaseout_amount_cap = phaseout.cap * max_(0, c21060 - nonlimited)
        uncapped_phaseout = max_(
            0,
            (
                (tax_unit("posagi", period) - phaseout.start[mars])
                * phaseout.rate
            ),
        )
        return min_(
            uncapped_phaseout,
            phaseout_amount_cap,
        )


class c04470(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Itemized deductions after phase-out"
    unit = USD
    documentation = (
        "Itemized deductions after phase-out (zero for non-itemizers)"
    )

    def formula(tax_unit, period, parameters):
        return max_(0, tax_unit("c21060", period) - tax_unit("c21040", period))
