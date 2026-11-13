from policyengine_us.model_api import *


class pays_aca_premium(Variable):
    value_type = bool
    entity = Person
    label = "Person pays an ACA marketplace premium"
    definition_period = YEAR
    reference = (
        # Marketplace enrollment itself has no income minimum.
        "https://www.law.cornell.edu/cfr/text/45/155.305#a",
        # The premium tax credit's income floor, and the below-poverty
        # exception for lawfully present immigrants.
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
    )
    documentation = (
        "Whether a person is enrolled in a Marketplace plan and charged an "
        "age-rated premium for it. This is an enrollment test, not a pure "
        "status test: alongside the TIN, immigration-status, other-minimum-"
        "essential-coverage and age-based premium conditions, it excludes the "
        "Medicaid coverage gap, so it carries an income component. "
        "45 CFR 155.305(a) sets no income minimum for enrolling, so a person "
        "in the gap may buy a plan at full price; the model assumes none "
        "does, because the unsubsidized benchmark premium exceeds their "
        "income (policyengine-us #9472). A reader that wants the status and "
        "coverage conditions without that assumption should not reuse this "
        "variable. It is is_aca_marketplace_enrollee restricted to people "
        "charged an age-rated premium: adults, and the three oldest "
        "enrolled children in the tax unit."
    )

    def formula(person, period, parameters):
        # An enrollee pays an age-rated premium unless they are a child
        # beyond the three oldest covered children (45 CFR 147.102(c)(1)).
        enrollee = person("is_aca_marketplace_enrollee", period)
        p = parameters(period).gov.aca
        is_aca_adult = person("age", period) > p.slcsp.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        return enrollee & (is_aca_adult | child_pays)
