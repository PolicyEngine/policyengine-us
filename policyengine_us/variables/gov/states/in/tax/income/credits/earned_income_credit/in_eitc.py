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
        if str(period) == "2021":
            # ... additional decoupling of parameters for childless taxpayers
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
