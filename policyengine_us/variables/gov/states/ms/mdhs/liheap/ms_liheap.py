from policyengine_us.model_api import *


class ms_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Mississippi LIHEAP regular energy assistance"
    documentation = (
        "Regular assistance with the main heating fuel bill and, for homes not "
        "heated by electricity, the electric bill. Verified for FY2026. Earlier "
        "years use model parameter backfilling and are unverified historical "
        "estimates."
    )
    defined_for = "ms_liheap_eligible"
    reference = (
        # Rule 7.4 A (page 36), Rule 7.8 A-D (page 39) and the Appendix benefit
        # matrix (pages 59-64).
        "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=39",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.mdhs.liheap
        size = spm_unit("ms_liheap_household_size", period)
        income = spm_unit("ms_liheap_income", period)
        # Rule 7.8 A pays from the attached matrix (manual PDF pages 59-64). The
        # income bands are encoded as published: the matrix prints a $31,313
        # fifth-band top for size 3, a $35,325 second-band top for size 10, five
        # bands for size 8 and four for size 12.
        band = 0
        for table_size in range(1, int(p.maximum_table_size) + 1):
            band = where(
                size == table_size,
                p.income_bands[str(table_size)].calc(income, right=True),
                band,
            )
        fuel = spm_unit("heating_type", period)
        types = fuel.possible_values
        reductions = max_(band - 1, 0)
        # Each column steps down by a fixed amount per income band, so a
        # first-band cap and a reduction per fuel reproduce the published cells.
        # The one exception is propane at size 16, band 4: the matrix prints
        # $350; encoded as published.
        fuel_cap = p.maximum_payment[fuel] - reductions * p.payment_reduction[fuel]
        exception = (
            (fuel == types.PROPANE)
            & (size == p.propane_exception_household_size)
            & (band == p.propane_exception_income_band)
        )
        fuel_cap = where(exception, p.propane_exception_amount, fuel_cap)
        # Rule 7.4 A pays the amount of the bill and Rule 7.8 C caps it by energy
        # type. Annual expenses approximate the bills presented during the program
        # year; prior awards, per-delivery propane limits, and prepaid-account
        # rules are not represented.
        heating_payment = min_(fuel_cap, max_(spm_unit("heating_expense", period), 0))
        # Rule 7.8 D: a total electric household receives the Total Electric
        # column, which is its fuel cap above. "All other households may receive
        # a total of the electric column and the main heating source column that
        # is used." The two caps together never exceed the Maximum Benefit column,
        # which equals the propane and electric columns combined. heating_type
        # ELECTRICITY stands for a total electric household. SOLAR and NONE have
        # no fuel column in the matrix, so they receive the electric column only.
        # An unspecified fuel is paid only when heat is included in rent.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        receives_electric_column = (fuel != types.ELECTRICITY) & (
            (fuel != types.UNSPECIFIED) | heat_in_rent
        )
        electric_cap = (
            p.electric_maximum_payment - reductions * p.electric_payment_reduction
        )
        electricity = max_(spm_unit("pre_subsidy_electricity_expense", period), 0)
        electric_payment = where(
            receives_electric_column, min_(electric_cap, electricity), 0
        )
        # A household with heat included in rent is eligible but receives $0 for
        # the heating column: Rule 6.4 A (manual PDF page 24) pays the energy
        # charge itemized in the lease and Rule 6.4 B pays $100 per intake up to
        # the matrix amount, and neither the itemized charge nor the number of
        # intakes is an input.
        # Source gaps (sizes 11/15 and upper ranges for 10/18/20) and sizes above
        # 20 also return zero as coverage gaps, not legal ineligibility.
        return where(band > 0, heating_payment + electric_payment, 0)
