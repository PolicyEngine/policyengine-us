from policyengine_us.model_api import *


class ca_yctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "California Young Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.1",
        "https://www.ftb.ca.gov/forms/2021/2021-3514-instructions.html",
        "https://www.ftb.ca.gov/forms/2021/2021-3514.pdf#page=3",
        "https://www.ftb.ca.gov/forms/2022/2022-3514-instructions.html",
        "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=3",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.ca.tax.income.credits.young_child

        # determine eligibility, which requires both (a) and (b) to be true:
        # (a) tax unit has at least one CalEITC-qualifying child
        # (b) tax unit receives CalEITC _OR_ is CalEITC eligible but has losses
        # ... determine (a)
        meets_age_limit = person("age", period) < p.ineligible_age
        is_qualifying_child_for_caleitc = person(
            "ca_is_qualifying_child_for_caleitc", period
        )
        is_eligible_child = meets_age_limit & is_qualifying_child_for_caleitc
        has_eligible_child = tax_unit.any(is_eligible_child)
        # ... determine (b) part one
        gets_caleitc = tax_unit("ca_eitc", period) > 0
        # ... determine (b) part two
        is_caleitc_eligible = tax_unit("ca_eitc_eligible", period)
        # ... ... R&TC 17052.1(b)(1)(B)(i): earned income of zero or less,
        # measured as the CalEITC earned income on FTB 3514 line 19, so a
        # business loss that offsets wages counts (Step 8).
        has_no_earned_income = tax_unit("ca_eitc_earned_income", period) <= 0
        # ... ... (B)(ii): net losses within the threshold. FTB 3514 line 23b
        # measures the net loss from Form 540 line 17 without utilization
        # limitations, so the capital loss limit does not apply. AGI carries
        # loss_limited_net_capital_gains, which already includes capital gain
        # distributions (they net against losses on Schedule D line 13), so the
        # unlimited amount adds them back to net_capital_gains as well.
        limited_capital_gains = tax_unit("loss_limited_net_capital_gains", period)
        distributions = tax_unit.sum(max_(0, person("non_sch_d_capital_gains", period)))
        unlimited_capital_gains = tax_unit("net_capital_gains", period) + distributions
        total_income = (
            tax_unit("ca_agi", period) - limited_capital_gains + unlimited_capital_gains
        )
        total_net_loss = max_(0, -total_income)
        has_limited_losses = total_net_loss <= p.loss_threshold
        # ... ... (B)(iii): wages, salaries, tips, and other employee
        # compensation within the same threshold (FTB 3514 line 23a, which
        # carries the filers' wages from line 13)
        wages = tax_unit_non_dep_sum("employment_income", tax_unit, period)
        has_limited_wages = wages <= p.loss_threshold
        # ... ... combine all the (b) elements where appropriate
        is_loss_eligible = where(
            p.loss_threshold > 0,
            is_caleitc_eligible
            & has_no_earned_income
            & has_limited_losses
            & has_limited_wages,
            False,
        )
        # ... combine (a) and (b) parts to determine eligibility
        eligible = has_eligible_child & (gets_caleitc | is_loss_eligible)

        # phase out credit amount
        # FTB 3514 line 23: YCTC earned income is the CalEITC line 19 amount.
        eitc_earnings = tax_unit("ca_eitc_earned_income", period)
        excess_earnings = max_(0, eitc_earnings - p.phase_out.start)
        increments = excess_earnings / p.phase_out.increment
        reduction = increments * p.phase_out.amount

        return eligible * max_(0, p.amount - reduction)
