from policyengine_us.model_api import *


class ar_federal_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Child and Dependent Care Credit replicated to include Arkansas limitations"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-502/",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2021_AR2441_Child_andDependentCareExpenses.pdf#page=1",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        # Ark. Code Ann. § 26-51-502(b)(1) adopts IRC § 21 as in effect on
        # January 2, 2013, a static-conformity snapshot that governs every
        # year the credit applies to. We pin the federal CDCC parameters to
        # the 2020 instant, whose values are identical to the January 2, 2013
        # law ($3,000/$6,000 caps, 35-to-20 percent rate, no second phase-out)
        # and predate both ARPA's 2021 expansion and the scheduled 2026
        # federal change, neither of which a static-conformity state adopts.
        # Same pinning pattern as va_child_dependent_care_deduction_cdcc_limit
        # and id_cdcc_limit.
        p = parameters("2020-01-01").gov.irs.credits.cdcc

        # AR2441 header: the IRC § 21(e)(2) and (4) special rules apply.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        # AR2441 lines 2-3: qualified expenses, capped per qualifying person.
        childcare = tax_unit("tax_unit_childcare_expenses", period)
        adult_care = add(tax_unit, period, ["care_expenses"])
        expenses = childcare + adult_care
        count_eligible = min_(
            p.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )
        capped_expenses = min_(expenses, p.max * count_eligible)
        # AR2441 lines 4-6: cap at the lower of head and spouse earnings.
        relevant_expenses = min_(
            capped_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # AR2441 lines 7-8: the rate phases from 35 to 20 percent of the
        # smallest amount as adjusted gross income rises; the 2013-law
        # schedule has no second phase-out.
        agi = tax_unit("adjusted_gross_income", period)
        excess_agi = max_(0, agi - p.phase_out.start)
        increments = np.ceil(excess_agi / p.phase_out.increment)
        rate = max_(p.phase_out.min, p.phase_out.max - increments * p.phase_out.rate)
        return eligible * relevant_expenses * rate
