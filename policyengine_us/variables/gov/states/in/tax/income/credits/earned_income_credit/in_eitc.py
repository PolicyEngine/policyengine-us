from policyengine_us.model_api import *


class in_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana earned income tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21"
    defined_for = "in_eitc_eligible"

    def formula(tax_unit, period, parameters):
        ip = parameters(period).gov.states["in"].tax.income.credits
        if not ip.earned_income.decoupled:
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * ip.earned_income.match_rate
        if ip.earned_income.static_conformity_in_effect:
            # Schedule IN-EIC (State Form 49469) Section A applies to every
            # filer: "Enter the earned income credit from your federal
            # income tax return," multiplied by 10%. There is no frozen-IRC
            # recomputation on the form. Section B is a qualifying-child
            # information schedule (names, SSNs, ages), not a computation
            # path, so it does not carve out childless filers.
            #
            # DOR Information Bulletin #92 describes the IRC section 32
            # January 1, 2023 conformity freeze (IC 6-3-1-11) uniformly for
            # "the Indiana EITC," with no childless-specific language. The
            # ARPA childless EITC expansion expired January 1, 2022, so for
            # TY2023 onward the freeze's only operative effect is that
            # Indiana does not automatically adopt post-snapshot federal
            # EITC changes -- and those changes are inflation indexing only.
            # The current-year federal EITC therefore satisfies the freeze
            # for all filers, with or without children.
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * ip.earned_income.match_rate
        # if Indiana EITC is decoupled from federal EITC
        fp = parameters(period).gov.irs.credits
        # ... cap child count
        kid_cap = ip.earned_income.max_children
        kids = min_(kid_cap, tax_unit("eitc_child_count", period))
        # ... specify decoupled parameter values
        maximum = fp.eitc.max.calc(kids)
        pi_rate = fp.eitc.phase_in_rate.calc(kids)
        po_start = fp.eitc.phase_out.start.calc(kids)  # no JOINT bonus
        po_rate = fp.eitc.phase_out.rate.calc(kids)
        if ip.earned_income.childless.in_effect:
            # 2021-only decoupled-childless-parameter branch, gated by
            # gov.states.in.tax.income.credits.earned_income.childless.in_effect.
            maximum0 = ip.earned_income.childless.maximum
            pi_rate0 = ip.earned_income.childless.phase_in_rate
            po_start0 = ip.earned_income.childless.phase_out_start
            po_rate0 = ip.earned_income.childless.phase_out_rate
            # ... integrate in childless parameters
            maximum = where(kids == 0, maximum0, maximum)
            pi_rate = where(kids == 0, pi_rate0, pi_rate)
            po_start = where(kids == 0, po_start0, po_start)
            po_rate = where(kids == 0, po_rate0, po_rate)
        # ... calculate eitc phase-in amount
        earnings = tax_unit("filer_adjusted_earnings", period)
        phase_in_amount = min_(earnings * pi_rate, maximum)
        # ... calculate eitc reduction
        federal_agi = tax_unit("adjusted_gross_income", period)
        higher_income = max_(earnings, federal_agi)
        reduction = po_rate * max_(0, higher_income - po_start)
        # ... calculate decoupled eitc amount
        amount = min_(phase_in_amount, max_(0, maximum - reduction))
        # ... match decoupled eitc amount to get Indiana eitc
        return amount * ip.earned_income.match_rate
