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
        p = parameters(period).gov.states.ca.tax.income.credits.young_child
        # determine eligibility, which requires both (a) and (b):
        # (a) tax unit receives CalEITC or is CalEITC eligible but has losses
        # (b) tax unit has at least one CalEITC-qualifying child
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.ineligible_age
        is_qualifying_child_for_caleitc = person(
            "ca_is_qualifying_child_for_caleitc", period
        )
        is_eligible_child = meets_age_limit & is_qualifying_child_for_caleitc
        has_eligible_child = tax_unit.sum(is_eligible_child) > 0

        gets_caleitc = tax_unit("ca_eitc", period) > 0

        is_loss_eligible = False

        eligible = has_eligible_child & (gets_caleitc | is_loss_eligible)

        # phase out credit amount
        eitc_earnings = tax_unit("filer_earned", period)
        excess_earnings = max_(0, eitc_earnings - p.phase_out.start)
        increments = excess_earnings / p.phase_out.increment
        reduction = increments * p.phase_out.amount
        return eligible * max_(0, p.amount - reduction)
