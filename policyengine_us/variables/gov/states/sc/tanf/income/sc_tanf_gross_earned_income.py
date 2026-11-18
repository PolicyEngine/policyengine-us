from policyengine_us.model_api import *


class sc_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        # Sections 7.1, 7.5, 7.7 and 8.16 B
        # PDF pages 102, 105, 112, 117, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=102",
        "https://www.scstatehouse.gov/coderegs/Chapter%20114.pdf#page=213",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned
        earned = add(person, period, p.earned)
        # Section 7.7 excludes the income of SSI recipients. 114-1140(N)(1)
        # excludes "the earned income of dependent children" in "the FI gross
        # income limit test and the need and benefit determination", as do
        # Sections 7.5 and 8.16 B, so neither income test counts it.
        counted = ~person("sc_tanf_ssi_recipient", period) & ~person(
            "sc_tanf_dependent_child", period
        )
        return earned * counted
