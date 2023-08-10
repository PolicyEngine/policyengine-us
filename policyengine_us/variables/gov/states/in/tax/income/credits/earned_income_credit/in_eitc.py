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
        ip = parameters(period).gov.states["in"].tax.income
        if not ip.credits.earned_income.decoupled:
            federal_eitc = tax_unit("earned_income_tax_credit", period)
            return federal_eitc * ip.credits.earned_income.match_rate
        # if Indiana EITC is decoupled from federal EITC
        fp = parameters(period).gov.irs.credits
        # ... cap child count
        kids = min_(2, tax_unit("eitc_child_count", period))  # <<<<<<<<<<<<<
        # ... set maximum "federal" eitc amount
        maximum = fp.eitc.max.calc(kids)
        #print("\nkids,maximum", kids, maximum)
        # ... set "federal" eitc phase-in rate
        pi_rate = fp.eitc.phase_in_rate.calc(kids)
        # ... set "federal" eitc phase-in amount
        earnings = max_(0, tax_unit("filer_earned", period))
        phase_in_amount = min_(earnings * pi_rate, maximum)
        # ... set "federal" eitc phase-out start with no JOINT bonus
        po_start = fp.eitc.phase_out.start.calc(kids)
        # ... set "federal" eitc phase-out rate
        po_rate = fp.eitc.phase_out.rate.calc(kids)
        #print("po_start,po_rate", po_start, po_rate)
        # ... set "federal" eitc reduction
        federal_agi = tax_unit("adjusted_gross_income", period)
        higher_income = max_(earnings, federal_agi)
        reduction = po_rate * max_(0, higher_income - po_start)
        # ... compute decoupled "federal" eitc amount
        amount = min_(phase_in_amount, max_(0, maximum - reduction))
        #print("reduction,amount", reduction, amount)
        # ... match "federal" eitc amount to get Indiana eitc
        return amount * ip.credits.earned_income.match_rate
