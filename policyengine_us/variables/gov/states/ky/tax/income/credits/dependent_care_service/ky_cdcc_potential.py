from policyengine_us.model_api import *


class ky_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kentucky household and dependent care service credit"
    documentation = (
        "Kentucky matches the federal credit allowed under its conformed "
        "Internal Revenue Code. For 2021, the December 31, 2018 reference "
        "excludes ARPA's expanded expense limits, rates, benefit exclusion "
        "and refundability. The credit is recomputed under that Code before "
        "applying Kentucky's match."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=29058",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=57913#page=3",
        # 2021 KRS 141.010(21)(b): December 31, 2018 conformity.
        "https://apps.legislature.ky.gov/law/acts/21RS/documents/0031.pdf#page=3",
        # The 2022 amendment advances conformity for taxable years from 2022.
        "https://apps.legislature.ky.gov/law/acts/22RS/documents/0212.pdf#page=62",
        # PDF pages 1-3: IRC 21(a)-(d) cap, rate, earnings limits, and
        # amendment history confirming these provisions were unchanged in 2018.
        "https://www.govinfo.gov/content/pkg/USCODE-2020-title26/pdf/USCODE-2020-title26-subtitleA-chap1-subchapA-partIV-subpartA-sec21.pdf#page=1",
        # PDF pages 1-3: conformed credit computation, section 129 benefit
        # reconciliation, and federal liability limit; instructions exclude ARPA.
        "https://revenue.ky.gov/Forms/2441-K-2021.pdf#page=1",
    )
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ky.tax.income
        # Kentucky matches the federal credit taken. KRS 141.067 sets the credit
        # at 20% of "the federal credit allowed under Section 21 of the Internal
        # Revenue Code," and KRS 141.010(21) fixes that Code at a reference
        # date. Where the reference date predates the One Big Beautiful Bill
        # Act, Kentucky's section 21 excludes the Act's rate increase. From
        # 2026 the reference date is December 31, 2025, which includes it.
        if p.irc_conformity.obbba:
            federal_credit = tax_unit("cdcc", period)
        else:
            federal_credit = tax_unit("pre_obbba_cdcc", period)
        return federal_credit * p.credits.dependent_care_service.match

    def formula_2021_01_01(tax_unit, period, parameters):
        # The December 31, 2018 Code excludes both ARPA's section 21 expansion
        # and section 129 exclusion increase. The 2020 parameters preserve
        # these unchanged pre-ARPA provisions without changing federal 2021.
        frozen = parameters("2020-01-01").gov.irs
        p = frozen.credits.cdcc
        childcare = tax_unit("cdcc_qualifying_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = max_(childcare + adult_care, 0)
        earnings = max_(tax_unit("min_head_spouse_earned", period), 0)

        # Form 2441-K Part III lines 18-29 limit excluded/deductible benefits
        # to benefits received, qualifying expenses, earnings, and $5,000
        # ($2,500 for a married separate filer not treated as unmarried).
        benefits = max_(add(tax_unit, period, ["dependent_care_employer_benefits"]), 0)
        exclusion_caps = frozen.gross_income.dependent_care_assistance_programs
        filing_status = tax_unit("filing_status", period)
        treated_as_unmarried = tax_unit("cdcc_treated_as_unmarried", period)
        exclusion_cap = where(
            treated_as_unmarried,
            exclusion_caps.reduction_amount["SINGLE"],
            exclusion_caps.reduction_amount[filing_status],
        )
        exclusion = min_(benefits, min_(expenses, min_(earnings, exclusion_cap)))

        # Lines 28-32 reduce both the conformed $3,000/$6,000 expense cap
        # and qualified expenses by these excluded/deductible benefits.
        qualifying_count = min_(
            tax_unit("capped_count_cdcc_eligible", period), p.eligibility.max
        )
        expense_limit = max_(p.max * qualifying_count - exclusion, 0)
        creditable_expenses = min_(
            expense_limit, min_(max_(expenses - exclusion, 0), earnings)
        )

        # Part II line 8: 35%, less one point for every started $2,000 over
        # $15,000, floored at 20%. The conformed Code has no second phaseout.
        agi = tax_unit("adjusted_gross_income", period)
        increments = np.ceil(max_(agi - p.phase_out.start, 0) / p.phase_out.increment)
        rate = max_(p.phase_out.min, p.phase_out.max - increments * p.phase_out.rate)
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        potential = eligible * creditable_expenses * rate
        # Part II lines 10-12: apply the federal liability limit first, then
        # Kentucky's 20% match. ARPA's federal refundability does not apply.
        federal_credit = min_(potential, tax_unit("cdcc_credit_limit", period))
        match = parameters(
            period
        ).gov.states.ky.tax.income.credits.dependent_care_service.match
        return federal_credit * match

    def formula_2022_01_01(tax_unit, period, parameters):
        # ARPA's temporary expansion has ended; retain the ordinary
        # computation and subsequent conformity changes from 2022 onward.
        return ky_cdcc_potential.formula(tax_unit, period, parameters)
