from policyengine_us.model_api import *


class nd_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "North Dakota LIHEAP regular heating assistance"
    reference = (
        "https://www.nd.gov/dhs/policymanuals/415/415_20_05_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_05.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_30.htm",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_15_01.htm",
    )
    defined_for = "nd_liheap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.liheap
        share = spm_unit("nd_liheap_share", period)
        fuel = spm_unit("heating_type", period)
        direct_payment = max_(spm_unit("heating_expense", period), 0) * share
        # Renter payments use the 415-30-30 monthly table amounts (share times
        # the fuel's yearly cap over 12), which keep 415-30-05's 45%-100% range.
        renter_cap = p.renter_annual_cap[fuel]
        # Shares are published as integer percentages. Recover that precision
        # after the float32 variable read so the oil 45% tie remains $82.50.
        share_percent = np.rint(share * 100)
        # Half-up(cap * share / 12) reproduces every published monthly cell.
        # This rounding order is inferred from the table, not stated in prose.
        monthly_renter_payment = np.floor(
            renter_cap * share_percent / (100 * MONTHS_IN_YEAR) + 0.5
        )
        renter_payment = min_(monthly_renter_payment * MONTHS_IN_YEAR, renter_cap)
        # UNSPECIFIED renter fuel has no supported amount. Its zero calculation
        # is a missing-input limitation, not a legal denial of renter benefits.
        # Annual inputs assume a full eligible year. Secondary heating and
        # nonresidential-use caps need distinctions absent from current inputs.
        # Current operational rules supersede the plan's conflicting 6%-income
        # and $7,500 narrative; neither is applied to ordinary residential bills.
        return where(
            spm_unit("heat_expense_included_in_rent", period),
            renter_payment,
            direct_payment,
        )
