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
        "https://codes.ohio.gov/assets/laws/administrative-code/pdfs/5180/2/16/5180$2-16-05_PH_FF_A_APP5_20221201_0903.pdf",
    )

    def formula(spm_unit, period, parameters):
        # 5180:2-16-05(B): the copayment is computed from the family's
        # poverty-band maximum income, not its actual income.
        p = parameters(period).gov.states.oh.dcy.ccap.copay
        # oh_ccap_fpg is the October-vintage monthly FPG per PL 21.
        fpg_monthly = spm_unit("oh_ccap_fpg", period)
        countable_income = spm_unit("oh_ccap_countable_income", period)
        # Net losses are already floored per person in
        # oh_ccap_countable_income; this floor defensively covers any other
        # negative income so it cannot produce a negative copayment.
        monthly_income = max_(countable_income, 0)
        # (B)(1)-(2): annualize income and divide by the annual FPG to get the
        # family's percentage of the federal poverty level.
        fpg_annual = fpg_monthly * MONTHS_IN_YEAR
        annual_income = monthly_income * MONTHS_IN_YEAR
        fpl_ratio = where(fpg_annual > 0, annual_income / fpg_annual, 0)
        # (B)(3): round the FPL ratio up to the next five per cent. The
        # increment's spacing must stay in lockstep with the threshold spacing
        # in copay/multiplier.yaml (1.05, 1.10, ...). Those thresholds are
        # shifted down by 1e-4 so that a ratio rounded exactly onto a 5% band
        # (which float32 stores as e.g. 1.0499999) still lands in that band
        # rather than the prior one.
        rounded_ratio = np.ceil(fpl_ratio / p.rounding_increment) * p.rounding_increment
        # PL 21's desk aid makes each band inclusive of its rounded-up dollar
        # endpoint (a family at exactly a band's published maximum stays in
        # that band), so step down one band when income also fits the
        # previous band's ceiled dollar maximum.
        previous_ratio = max_(rounded_ratio - p.rounding_increment, 0)
        previous_band_max = np.ceil(previous_ratio * fpg_annual / MONTHS_IN_YEAR)
        rounded_ratio = where(
            monthly_income <= previous_band_max, previous_ratio, rounded_ratio
        )
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
        # (A)(3)(a): families at or below 100% FPG have a zero copayment;
        # per the PL 21 desk aid the 100% standard is the ceiled dollar
        # amount.
        waiver_income_limit = np.ceil(
            p.fpl_waiver_threshold * fpg_annual / MONTHS_IN_YEAR
        )
        weekly_copay = where(monthly_income <= waiver_income_limit, 0, weekly_copay)
        # The model assumes one family care arrangement and retains the
        # pre-distribution family copay.
        # Convert the weekly copay to a monthly amount for the MONTH-period
        # benefit (WEEKS_IN_YEAR weeks per year, MONTHS_IN_YEAR months).
        monthly_copay = weekly_copay * WEEKS_IN_YEAR / MONTHS_IN_YEAR
        protective = spm_unit("oh_ccap_protective_care", period)
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return where(protective | is_homeless, 0, monthly_copay)
