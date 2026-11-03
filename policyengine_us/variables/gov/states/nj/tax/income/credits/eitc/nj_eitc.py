from policyengine_us.model_api import *


class nj_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-7/",
        # P.L. 2021, c.130, section 1a(1) and (4).
        "https://pub.njleg.state.nj.us/Bills/2020/PL21/130_.HTM",
        # 2025 NJ-1040 instructions, line 58.
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=44",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get parameter tree for NJ EITC.
        p = parameters(period).gov.states.nj.tax.income.credits.eitc
        # Get parameter tree for federal EITC.
        p_fed = parameters(period).gov.irs.credits.eitc

        # Calculate NJ EITC.
        # If eligible for federal EITC, return federal EITC * percent_of_federal_eitc.
        # If ineligible for federal EITC only because of age, return (max federal EITC for zero children) * percent_of_federal_eitc.
        #     Note: this implies that they have no children.
        # Otherwise, return 0.

        # Section 1a(1): a percentage "of the federal earned income tax credit
        # that would be allowed". The federal credit already reflects its
        # phase-in, phase-out, take-up and filing, so a federally eligible
        # filer gets the match on it, whatever its size. The select below
        # takes this path first, so such a filer never reaches the age path.
        federal_eitc_eligible = tax_unit("eitc_eligible", period)

        # Section 1a(4): a childless filer "ineligible to claim the federal
        # earned income tax credit due to age requirements" gets the match on
        # "the federal maximum amount for taxpayers with no qualifying child"
        # (2025 NJ-1040 line 58: "enter $260", 40% of $649). The filer must
        # still meet the federal earned income and AGI limits, so the federal
        # credit recomputed without the age test must be positive. Comparing the phase-in amount with the
        # reduction instead would deny the credit to a low earner whose
        # unearned income puts the reduction above the phase-in amount but
        # below the maximum.
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        meets_federal_income_limits = min_(phased_in, max_(0, maximum - reduction)) > 0
        childless_eitc_eligible = (
            tax_unit("nj_childless_eitc_age_eligible", period)
            & meets_federal_income_limits
        )
        federal_eitc = select(
            [
                federal_eitc_eligible,
                childless_eitc_eligible,
            ],
            [
                tax_unit("eitc", period),
                p_fed.max.calc(0),
            ],
            default=0,
        )

        return federal_eitc * p.match
