from policyengine_us.model_api import *


class sc_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "South Carolina TANF gross earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.SC
    # PDF pages 102, 112, 117
    reference = "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=102"  # Sections 7.1 and 7.7

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tanf.income.earned
        earned = add(person, period, p.earned)
        # Section 7.7 excludes the income of SSI recipients.
        return earned * ~person("sc_tanf_ssi_recipient", period)
