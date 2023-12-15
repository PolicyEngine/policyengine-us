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
        # ... ... determine if losses are limited to modest amount
        federal_gross_income = add(tax_unit, period, ["irs_gross_income"])
        total_federal_net_loss = max_(0, -federal_gross_income)
        has_limited_losses = total_federal_net_loss <= p.loss_threshold
        # ... ... determine if earnings are limited to modest amount
        total_earnings = tax_unit("tax_unit_earned_income", period)
        has_limited_earnings = total_earnings <= p.loss_threshold
        # ... ... combine all the (b) elements where appropriate
        is_loss_eligible = where(
            p.loss_threshold > 0,
            is_caleitc_eligible & has_limited_losses & has_limited_earnings,
            False,
        )
        # ... combine (a) and (b) parts to determine eligibility
        eligible = has_eligible_child & (gets_caleitc | is_loss_eligible)

        # phase out credit amount
        eitc_earnings = tax_unit("filer_adjusted_earnings", period)
        excess_earnings = max_(0, eitc_earnings - p.phase_out.start)
        increments = excess_earnings / p.phase_out.increment
        reduction = increments * p.phase_out.amount

        return eligible * max_(0, p.amount - reduction)
