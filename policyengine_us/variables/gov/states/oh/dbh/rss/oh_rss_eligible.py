from policyengine_us.model_api import *


class oh_rss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Ohio RSS categorical and placement requirements"
    definition_period = MONTH
    defined_for = StateCode.OH
    documentation = "Medicaid enrollment comes from medicaid_enrolled. If you enter it, enter it for every person in the simulation; an entry for one person sets everyone else to false."
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5122-36-02",
    )
    # NOTE: PolicyEngine's Ohio aged, blind or disabled Medicaid income limit is
    # the SSI benefit rate (5160:1-3-03.5(B)(3)), and it has no group for people
    # who receive only an optional state supplement. A person whose income is
    # above that rate therefore needs medicaid_enrolled entered.

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        return (
            person("oh_rss_certified", period)
            & (person("age", period.this_year) >= p.minimum_age)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & person("medicaid_enrolled_for_ssi_state_supplement", period.this_year)
        )
