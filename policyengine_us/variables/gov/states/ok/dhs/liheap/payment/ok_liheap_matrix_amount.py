from policyengine_us.model_api import *


class ok_liheap_matrix_amount(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP winter heating matrix amount"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a), (d).
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7-a.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/OK_BenefitMatrix_2026.docx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.payment
        size = spm_unit("ok_liheap_household_size", period)
        # OAC 340:20-1-11(a) rounds monthly income to the nearest dollar, and
        # Appendix C-7-A prints whole-dollar bands, so round half up first.
        net_income = spm_unit("ok_liheap_net_income", period)
        monthly_income = np.floor(net_income / MONTHS_IN_YEAR + 0.5)
        band = p.income_band.calc(max_(monthly_income, 0)).astype(int)
        size_group = p.household_size_group.calc(max_(size, 1)).astype(int)
        fuel = spm_unit("heating_type", period)
        fuels = fuel.possible_values
        ordinary_fuel = (
            (fuel == fuels.NATURAL_GAS)
            | (fuel == fuels.ELECTRICITY)
            | (fuel == fuels.WOOD)
            | (fuel == fuels.COAL)
        )
        delivered_fuel = (
            (fuel == fuels.PROPANE)
            | (fuel == fuels.FUEL_OIL)
            | (fuel == fuels.KEROSENE)
        )
        direct_payment = select(
            [ordinary_fuel, delivered_fuel],
            [p.matrix.ordinary[band][size_group], p.matrix.delivered[band][size_group]],
            # OTHER, SOLAR and UNSPECIFIED have no supported direct-payment
            # mapping. Zero is an unverified estimate, not a legal denial.
            default=0,
        )
        dwelling = spm_unit("ok_liheap_dwelling_type", period)
        roomer = dwelling == dwelling.possible_values.ROOMER
        rent_payment = where(
            roomer,
            p.matrix.roomer[band][size_group],
            p.matrix.renter[band][size_group],
        )
        # Heat-in-rent schedules cover every fuel. Eligibility separately needs
        # a positive surcharge bill, which an unknown fuel cannot carry.
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        amount = where(heat_in_rent, rent_payment, direct_payment)
        # The matrix has no actual-expense cap. Gross eligibility and heating
        # responsibility are applied by the final award variable.
        return where((size > 0) & (fuel != fuels.NONE), amount, 0)
