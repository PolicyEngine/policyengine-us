from policyengine_us.model_api import *


class sc_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 102, 105, 112, 117, 134
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=102"  # Sections 7.1, 7.5, 7.7 and 8.16 B

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned
        earned = add(person, period, p.earned)
        # Section 7.7 excludes the income of SSI recipients. Section 7.5
        # excludes a dependent child's earned income from eligibility and
        # the benefit, and Section 8.16 B leaves it out of the budget, so
        # neither the gross nor the net income test counts it.
        counted = ~person("sc_tanf_ssi_recipient", period) & ~person(
            "sc_tanf_dependent_child", period
        )
        return earned * counted
