from policyengine_us.model_api import *


class oh_rss_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Ohio RSS categorical and placement requirements"
    definition_period = MONTH
    defined_for = StateCode.OH
    documentation = "Medicaid enrollment comes from medicaid_enrolled. A candidate who meets SSI's criteria other than income but whose income is too high for SSI meets the Medicaid requirement through Ohio's group for people who receive only a state supplement, even when medicaid_enrolled is entered as false. If you enter medicaid_enrolled, enter it for every person in the simulation; an entry for one person sets everyone else to false."
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5160:1-5-01",
        "https://codes.ohio.gov/ohio-administrative-code/rule-5122-36-02",
        # PDF pages 17-18
        "https://www.medicaid.gov/State-resource-center/Medicaid-State-Plan-Amendments/Downloads/OH/OH-15-015.pdf#page=17",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.oh.dbh.rss
        # 5160:1-5-01(C)(1)(a) requires eligibility for medical assistance.
        # PolicyEngine's Ohio aged, blind or disabled Medicaid income limit is
        # the SSI benefit rate (5160:1-3-03.5(B)(3)). Ohio's state plan also
        # covers, under 42 CFR 435.232, people who receive only a state
        # supplement and "would be eligible for SSI except for the level of
        # their income", including aged, blind and disabled individuals in
        # group living arrangements (SPA 15-015, Attachment 2.2-A, pages
        # 15-16). RSS pays the difference between countable income and its
        # income standard in cash, so a candidate who meets SSI's other
        # criteria but whose income is too high for SSI meets the condition.
        medicaid = person(
            "medicaid_enrolled_for_ssi_state_supplement", period.this_year
        )
        state_supplement_only = person("is_ssi_eligible", period) & (
            person("uncapped_ssi", period) <= 0
        )
        return (
            person("oh_rss_certified", period)
            & (person("age", period.this_year) >= p.minimum_age)
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & (medicaid | state_supplement_only)
        )
