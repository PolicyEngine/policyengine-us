from openfisca_us.model_api import *
import numpy as np


class ca_young_child(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Young Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-3514.pdf#page=3",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.1",
        "https://www.ftb.ca.gov/forms/2021/2021-3514-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.young_child
        earnings = tax_unit("tax_unit_earned_income", period)

        # Eligibility requires
        # a) tax unit receives CalEITC
        # b) tax unit has at least one CalEITC-qualifying child under six
        person = tax_unit.members
        meets_age_limit = person("age", period) < p.ineligible_age
        is_qualifying_child_for_caleitc = person(
            "ca_is_qualifying_child_for_caleitc", period
        )
        is_eligible_child = meets_age_limit & is_qualifying_child_for_caleitc
        has_eligible_child = tax_unit.sum(is_eligible_child) > 0
        receives_ca_eitc = tax_unit("ca_eitc", period) > 0
        in_ca = tax_unit.household("state_code_str", period) == "CA"
        eligible = has_eligible_child & receives_ca_eitc & in_ca
        # Phase out the amount.
        # NB: Law and instructions say $20 per $100, but the tax form
        # instructs the filer to round.
        excess_earnings = max_(0, earnings - p.phase_out.start)
        # Round increments to two decimal places.
        increments = np.round_(excess_earnings / p.phase_out.increment, 2)
        # Round reduction to two decimal places.
        reduction = min_(
            p.amount, np.round_(increments * p.phase_out.amount, 2)
        )
        # Round final result to nearest dollar.
        # In reality, <$1 goes to $1.
        return eligible * np.rint(p.amount - reduction)
