from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_demographic_eligibility,
    calculate_eitc_like_amount,
)


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
            # IC 6-3-1-11 (Indiana's IRC definition for IC 6-3.1-21):
            #   - TY 2023 through 2025: IRC as in effect on January 1, 2023.
            #   - TY 2026 onward: IRC as in effect on January 1, 2026, per
            #     Indiana SEA 243 (2025).
            # The snapshot dates are statutory literals; policyengine-core
            # parameters do not support date-valued types, so they appear
            # here rather than in the parameter tree.
            snapshot_date = "2026-01-01" if period.start.year >= 2026 else "2023-01-01"
            frozen_eitc = parameters.gov.irs.credits.eitc(snapshot_date)
            child_count = tax_unit("eitc_child_count", period)
            demographic_eligible = calculate_eitc_demographic_eligibility(
                tax_unit, period, frozen_eitc, child_count
            )
            filer_identification_eligible = tax_unit(
                "filer_meets_eitc_identification_requirements", period
            )
            investment_income_eligible = (
                tax_unit("eitc_relevant_investment_income", period)
                <= frozen_eitc.phase_out.max_investment_income
            )
            frozen_federal_eitc = calculate_eitc_like_amount(
                tax_unit,
                period,
                parameters,
                child_count,
                demographic_eligible,
                filer_identification_eligible,
                separate_filer_eligible=frozen_eitc.eligibility.separate_filer,
                eitc_parameters=frozen_eitc,
                investment_income_eligible=investment_income_eligible,
            )
            return frozen_federal_eitc * ip.earned_income.match_rate
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
