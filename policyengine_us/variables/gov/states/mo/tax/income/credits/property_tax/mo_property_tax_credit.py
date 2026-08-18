from policyengine_us.model_api import *


class mo_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=57542",
        "https://dor.mo.gov/forms/Property%20Tax%20Claim%20Chart_2025.pdf#page=1",
    )
    defined_for = "mo_ptc_taxunit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        # Qualifying payment: 20% of gross rent (capped) plus property taxes,
        # subject to the combined property tax limit, per RSMo 135.010(7) and
        # 135.030.
        rent = add(tax_unit, period, ["rent"])
        rent_equivalent = min_(
            rent * p.property_tax_rent_ratio, p.rent_property_tax_limit
        )
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        payment = min_(
            rent_equivalent + min_(property_tax, p.property_tax_limit),
            p.property_tax_limit,
        )
        # DOR forms round entries half-up to whole dollars before table lookup.
        payment = np.floor(payment + 0.5)
        net_income = np.floor(tax_unit("mo_ptc_net_income", period) + 0.5)
        base = p.phase_out.threshold
        step = p.phase_out.step
        # RSMo 135.030(2)-(3): income at or below the minimum base receives
        # the actual capped payment; above it, the credit comes from the
        # director's table, which accumulates 1/16% per income increment (up
        # to the maximum rate) and computes at increment midpoints. The
        # statute says the result is rounded to the nearest whole dollar,
        # but the published DOR charts round the credit down (the phaseout
        # up); this formula reproduces every cell of the published charts.
        increments = np.ceil(max_(net_income - base, 0) / step)
        rate = min_(increments * p.phase_out.rate, p.phase_out.max_rate)
        # The final income increment is clipped at the upper income limit.
        income_limit = tax_unit("mo_ptc_income_limit", period)
        bracket_bottom = base + (increments - 1) * step
        bracket_top = min_(base + increments * step, income_limit)
        income_midpoint = (bracket_bottom + bracket_top) / 2
        phase_out = np.ceil(rate * income_midpoint)
        # Payment increments are anchored at the applicable cap; renter-only
        # units use the rent-equivalent cap.
        cap = where(property_tax > 0, p.property_tax_limit, p.rent_property_tax_limit)
        width = p.phase_out.payment_increment
        payment_steps = (cap - payment) // width
        payment_midpoint = cap - payment_steps * width - (width - 1) / 2
        table_credit = max_(payment_midpoint - phase_out, 0)
        return where(increments == 0, payment, table_credit)
