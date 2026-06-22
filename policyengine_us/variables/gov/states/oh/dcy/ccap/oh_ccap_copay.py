from policyengine_us.model_api import *


class oh_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Ohio CCAP family copayment"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-05",
        "https://codes.ohio.gov/assets/laws/administrative-code/pdfs/5180/2/16/5180$2-16-05_PH_FF_A_APP5_20221201_0903.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        # 5180:2-16-05(B): the copayment is computed from the family's
        # poverty-band maximum income, not its actual income.
        p = parameters(period).gov.states.oh.dcy.ccap.copay
        # spm_unit_fpg is the YEAR (annual) 100% FPG; the bare period
        # auto-divides it to a monthly value.
        fpg_monthly = spm_unit("spm_unit_fpg", period)
        countable_income = spm_unit("oh_ccap_countable_income", period)
        # Floor income at zero so a self-employment loss cannot produce a
        # negative copayment.
        monthly_income = max_(countable_income, 0)
        # (B)(1)-(2): annualize income and divide by the annual FPG to get the
        # family's percentage of the federal poverty level.
        fpg_annual = fpg_monthly * MONTHS_IN_YEAR
        annual_income = monthly_income * MONTHS_IN_YEAR
        fpl_ratio = where(fpg_annual > 0, annual_income / fpg_annual, 0)
        # (B)(3): round the FPL ratio up to the next five per cent.
        rounded_ratio = np.ceil(fpl_ratio / 0.05) * 0.05
        # (B)(4): the band's maximum monthly income is the rounded percentage
        # times the annual FPG, divided by twelve, rounded up to the nearest
        # dollar.
        band_max_monthly_income = np.ceil(rounded_ratio * fpg_annual / MONTHS_IN_YEAR)
        # (B)(5): multiply the band-maximum monthly income by the copay
        # multiplier, round to the nearest dollar, annualize, and divide by
        # the number of weeks in the state fiscal year for the weekly copay.
        multiplier = p.multiplier.calc(rounded_ratio)
        weekly_copay = (
            np.round(band_max_monthly_income * multiplier)
            * MONTHS_IN_YEAR
            / p.weeks_in_fiscal_year
        )
        # (A)(3)(a): families at or below 100% FPG have a zero copayment.
        weekly_copay = where(fpl_ratio <= p.fpl_waiver_threshold, 0, weekly_copay)
        # Convert the weekly copay to a monthly amount for the MONTH-period
        # benefit (WEEKS_IN_YEAR weeks per year, MONTHS_IN_YEAR months).
        monthly_copay = weekly_copay * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        # 5180:2-16-05(G): the copayment is waived for families receiving
        # protective or homeless child care.
        person = spm_unit.members
        protective = (
            spm_unit.sum(
                person("receives_or_needs_protective_services", period.this_year)
                | person("is_in_foster_care", period)
            )
            > 0
        )
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return where(protective | is_homeless, 0, monthly_copay)
