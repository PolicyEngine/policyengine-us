from policyengine_us.model_api import *


class ar_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP regular heating matrix amount"
    defined_for = StateCode.AR
    reference = (
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Electric.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Natural-Gas.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Propane.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Fuel-Oil.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2026_Other-Wood-Pellets.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Electric.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Natural-Gas.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Propane.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Fuel-Oil.pdf#page=1",
        # PDF pages 1-2
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/LIHEAP_Benefit-Matix_2025_Other-Wood-Pellets.pdf#page=1",
        # FY2025 plan item 2.6 benefit estimate.
        "https://liheapch.acf.gov/docs/2025/state-plans/AR_Plan_2025.pdf#page=9",
        # FY2025 electric matrix, Wayback capture of December 6, 2024.
        # PDF pages 1-2
        "https://web.archive.org/web/20241206194455id_/https://www.adeq.state.ar.us/energy/assistance/pdfs/liheap_benefit-matix_2025_electric.pdf#page=1",
        # Clearinghouse "2025" Arkansas matrix (FY2024 base amounts).
        # PDF pages 1-5
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/AR_BenefitMatrix_2025.pdf#page=1",
        # Application fuel groups.
        "https://www.adeq.state.ar.us/energy/assistance/pdfs/fillable_aeo-9495_liheap-long-application.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ee.aeo.liheap.payment
        income = spm_unit("ar_liheap_countable_income", period) / MONTHS_IN_YEAR
        size = spm_unit("ar_liheap_household_size", period)
        # Countable income is already rounded to whole monthly dollars, and
        # the printed lower bounds are inclusive: $70 starts the second band.
        band = p.income_band.calc(max_(income, 0)).astype(int)
        size_group = p.household_size_group.calc(max_(size, 1)).astype(int)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        # FY2025 cells follow AEO's matrices headed "(20% OVER BASE)", posted
        # before the season (the electric file, whose PDF metadata reads October
        # 7, 2024, is byte-identical to a December 6, 2024 Wayback capture), not
        # FY2025 plan item 2.6's $50 to $475 estimate (page 9). The Clearinghouse
        # "2025" Arkansas matrix repeats the FY2024 base amounts; 1.2 times them,
        # rounded, gives the FY2025 cells in the 35 rows whose lower bounds run
        # from $0 to $2,250. The top rows differ.
        amount = select(
            [
                fuel == fuels.ELECTRICITY,
                fuel == fuels.NATURAL_GAS,
                fuel == fuels.PROPANE,
                (fuel == fuels.FUEL_OIL) | (fuel == fuels.KEROSENE),
                (fuel == fuels.WOOD) | (fuel == fuels.COAL) | (fuel == fuels.OTHER),
            ],
            [
                p.matrix.electricity[band][size_group],
                p.matrix.natural_gas[band][size_group],
                p.matrix.propane[band][size_group],
                p.matrix.fuel_oil[band][size_group],
                p.matrix.other[band][size_group],
            ],
            # NONE has no heating. UNSPECIFIED and SOLAR have no supported
            # schedule mapping; zero is an unverified estimate, not a legal
            # eligibility determination, including when heat is in rent.
            default=0,
        )
        # This is the ungated table amount; ar_liheap applies eligibility.
        # The fixed regular schedule has no actual-expense cap.
        return where(size > 0, amount, 0)
