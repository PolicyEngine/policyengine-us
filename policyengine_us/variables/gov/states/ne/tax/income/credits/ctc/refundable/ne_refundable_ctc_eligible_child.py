from policyengine_us.model_api import *


class ne_refundable_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska refundable Child Tax Credit eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7202"
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        age_eligible = person("age", period) <= p.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)
        age_eligible_dependent = age_eligible & is_dependent
        # Nebraska limits the CTC to children who are either:
        # 1) enrolled in a child care program licensed pursuant to the Child Care
        #    Licensing Act
        # 2) receiving care from an approved license-exempt provider enrolled in
        #    the child care subsidy program pursuant to Neb. Rev. Stat. §§ 68-1202
        #    and 68-1206
        # As we do not yet model either the Child Care Licensing Act or the
        # Nebraska child care subsidy program, we approximate it as having incurred
        # pre-subsidy childcare expenses.
        received_qualifying_child_care = (
            person("pre_subsidy_childcare_expenses", period) > 0
        )
        income_eligible = person.tax_unit(
            "ne_refundable_ctc_income_eligible", period
        )
        return age_eligible_dependent & (
            received_qualifying_child_care | income_eligible
        )
