from policyengine_us.model_api import *


class mn_social_security_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota social security subtraction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Schedule M1M line 12. Minn. Stat. 290.0132, subd. 26(i) gives "
        "'Social Security benefits' the meaning in IRC 86(d)(1), so title II "
        "benefits and tier 1 railroad retirement benefits (the social security "
        "equivalent benefit) count together, as on Form 1040 lines 6a and 6b. "
        "The model subtracts the taxable tier 1 benefits with the rest of the "
        "railroad annuity (taxable_railroad_benefits, 45 U.S.C. 231m(a)), on "
        "Schedule M1M line 17, so this subtraction leaves them out as steps 26 "
        "to 29 of the line 12 worksheet direct."
    )
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.26",
        "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf",
        # 2022 Schedule M1M instructions, worksheet for line 12, steps 17-20.
        "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1m-22.pdf#page=4",
        # 2020 Schedule M1M instructions, line 39 worksheet, step 8: federal
        # Schedule 1 adjustments only, not Form 1040 line 10b.
        "https://www.revenue.state.mn.us/sites/default/files/2024-01/m1m_20.pdf#page=8",
        # 2025 Schedule M1M instructions, line 12 and its worksheet, steps
        # 1-30, and line 17.
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1m-25.pdf#page=4",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.subtractions.social_security
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        reduction_start = p.reduction.start[filing_status]
        reduction_applies = agi > reduction_start
        # Form 1040 line 6b (worksheet steps 6, 10 and 25): taxable title II
        # benefits and taxable tier 1 railroad retirement benefits.
        taxable_title_ii = add(tax_unit, period, ["taxable_social_security"])
        taxable_tier_1 = add(
            tax_unit,
            period,
            ["taxable_railroad_social_security_equivalent_benefits"],
        )
        taxable_benefits = taxable_title_ii + taxable_tier_1
        if p.reduction.applies:
            # Simplified subtraction, subd. 26(b) to (d). Steps 1-8 reduce
            # all taxable benefits; step 29 then takes out the tier 1
            # benefits that line 17 subtracts.
            reduction_increment = p.reduction.increment[filing_status]
            agi_excess = max_(0, agi - reduction_start)
            reduction_fraction = np.ceil(agi_excess / reduction_increment)
            reduction_rate = min_(p.reduction.rate * reduction_fraction, 1)
            reduced_benefits = max_(0, taxable_benefits * (1 - reduction_rate))
            simplified_subtraction = max_(0, reduced_benefits - taxable_tier_1)
        else:
            simplified_subtraction = 0
        # Alternate subtraction, subd. 26(e) to (h), on provisional income
        # (steps 9-19). Step 11 starts from total income less all taxable
        # benefits, and step 12 adds half of Form 1040 line 6a: the head's and
        # spouse's title II and tier 1 benefits. A dependent's benefits go on
        # the dependent's own return.
        income_amount = p.income_amount[filing_status]
        alt_amount = p.alternative_amount[filing_status]
        us_gross_income = add(tax_unit, period, ["irs_gross_income"])
        adj_income = us_gross_income - taxable_benefits
        section_86_benefits = tax_unit("tax_unit_section_86_benefits", period)
        benefit_amount = section_86_benefits * p.total_benefit_fraction
        tax_exempt_int = add(tax_unit, period, ["tax_exempt_interest_income"])
        sum_income = adj_income + benefit_amount + tax_exempt_int
        us_ald = tax_unit("above_the_line_deductions", period)
        student_loan_int = add(tax_unit, period, ["student_loan_interest"])
        # The 2020 worksheet's step 8 counts the Schedule 1 adjustments, so
        # not the 2020 charitable deduction for non-itemizers (Form 1040 line
        # 10b).
        charitable_ald = tax_unit("charitable_contributions_ald", period)
        mn_ald = max_(0, us_ald - student_loan_int - charitable_ald)
        income = max_(0, sum_income - mn_ald)
        net_income = max_(0, income - income_amount)
        alt_sub_amt = max_(0, alt_amount - (net_income * p.net_income_fraction))
        # Steps 25-28: the lesser of the maximum subtraction and the taxable
        # benefits other than the tier 1 benefits on line 17.
        alternate_subtraction = min_(taxable_title_ii, alt_sub_amt)
        if p.reduction.applies:
            # At or below the phase-out threshold, line 12 takes all of line
            # 6b, and line 17 then leaves out the tier 1 benefits; the model
            # subtracts those with the rest of the railroad annuity.
            return where(
                reduction_applies,
                max_(alternate_subtraction, simplified_subtraction),
                taxable_title_ii,
            )
        else:
            return max_(alternate_subtraction, simplified_subtraction)
