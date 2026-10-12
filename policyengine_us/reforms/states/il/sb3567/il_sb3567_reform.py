from policyengine_us.model_api import *


def create_il_sb3567() -> Reform:
    class il_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Illinois Child Tax Credit"
        unit = USD
        definition_period = YEAR
        # Bill text + the underlying state and federal statutes it builds on.
        reference = (
            # SB3567 bill text (104th GA), amending 35 ILCS 5/244(a).
            "https://www.ilga.gov/documents/legislation/104/SB/PDF/10400SB3567lv.pdf#page=2",
            # 35 ILCS 5/244 - Illinois Child Tax Credit (subsections (a) and (b)).
            "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K244",
            # 35 ILCS 5/212 - Illinois EITC, whose "maximum value" Section 244 references.
            "https://www.ilga.gov/legislation/ilcs/fulltext.asp?DocName=003500050K212",
            # IRC § 32 - federal EITC schedule whose phase-in plateau anchors
            # SB3567's "income threshold to qualify for the maximum federal EITC".
            "https://www.law.cornell.edu/uscode/text/26/32",
            # IRC § 152 - dependent definition cited by SB3567 Tier (1)-(2).
            "https://www.law.cornell.edu/uscode/text/26/152",
        )
        defined_for = StateCode.IL

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.il.tax.income.credits
            ctc = p.ctc
            person = tax_unit.members
            age = person("age", period)
            age_eligible_child = age < ctc.age_limit
            federal_ctc_eligible_child = person("ctc_qualifying_child", period)
            eligible_child = age_eligible_child & federal_ctc_eligible_child
            eligible_child_present = tax_unit.any(eligible_child)

            # The baseline IL CTC formula: 40% (rate) of the IL EITC (which
            # is itself a state match of the federal EITC).
            actual_credit = tax_unit("il_eitc", period) * ctc.rate

            # 35 ILCS 5/244(a) prescribes a flat 20% of Section 212 for
            # TY 2024 (no tier logic); the three-tier (a)(1)-(3) structure
            # applies only "for tax years beginning on or after
            # January 1, 2025." Preserve baseline behavior pre-2025.
            if period.start.year < 2025:
                return eligible_child_present * actual_credit

            # Tier (a)(1) and (a)(2) ceiling: 40% of "the maximum value of
            # the credit allowed under Section 212 of this Act based on the
            # number of qualifying dependents as defined by Section 152."
            #
            # KNOWN APPROXIMATION: IRC § 152 includes qualifying RELATIVES
            # and has no 3-child cap. We use `eitc_maximum` here, which is
            # keyed off federal § 32 EITC qualifying-child count (capped at
            # 3 by the federal schedule). This under-credits families with
            # (i) 4+ EITC-qualifying children or (ii) § 152 dependents who
            # are not § 32 qualifying children (e.g., an elderly dependent
            # parent). Pending sponsor clarification on whether SB3567
            # intends the broader § 152 universe or — as is conventional in
            # IL EITC linkage — the § 32 EITC-qualifying subset.
            federal_maximum = tax_unit("eitc_maximum", period)
            phase_in_rate = tax_unit("eitc_phase_in_rate", period)
            # SB3567 "income threshold to qualify for the maximum federal
            # EITC" is the end of the phase-in range / start of the plateau.
            # The federal phase-in threshold is an earned-income concept;
            # SB3567 explicitly tests against ADJUSTED GROSS INCOME, so we
            # compare AGI against the earned-income plateau-start value.
            # This produces conservative results when AGI > earned income
            # (e.g., filers with investment or retirement income).
            max_federal_eitc_threshold = federal_maximum / phase_in_rate
            max_credit = federal_maximum * p.eitc.match * ctc.rate

            agi = tax_unit("adjusted_gross_income", period)
            # Tier (a)(3) — AGI above the plateau-start — collapses
            # mathematically to `actual_credit` because at the plateau and
            # beyond, `il_eitc * ctc.rate` equals `max_credit`. We encode
            # this as the fall-through branch rather than a third explicit
            # arm; the math is equivalent at the boundary.
            return eligible_child_present * where(
                agi <= max_federal_eitc_threshold,
                max_credit,
                actual_credit,
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(il_ctc)

    return reform


def create_il_sb3567_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_il_sb3567()
    # Idiomatic single-period activation check, matching sibling contrib
    # reforms (pa_ctc_match, ct_sb100, ny/wftc). No 5-year forward
    # lookahead: that pattern can retroactively activate the reform in
    # earlier years when the toggle later flips, which is not desired here.
    if parameters(period).gov.contrib.states.il.sb3567.in_effect:
        return create_il_sb3567()
    return None


il_sb3567 = create_il_sb3567_reform(None, None, bypass=True)
