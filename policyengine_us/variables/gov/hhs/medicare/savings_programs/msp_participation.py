from policyengine_us.model_api import *


class msp_participation(Variable):
    value_type = bool
    entity = Person
    label = "Medicare Savings Program participation for an eligible person"
    definition_period = MONTH
    reference = (
        "https://www.cms.gov/files/document/chapter-1-program-overview-and-policy.pdf#page=20",
    )
    documentation = (
        "Participation gate, separate from financial and Medicare eligibility. "
        "Preserves the existing modeled SSI-related buy-in coverage when "
        "discretionary MSP take-up is false. This does not determine additional "
        "state buy-in eligibility; each coverage formula retains its existing "
        "eligibility rules."
    )

    def formula(person, period, parameters):
        takes_up = person("takes_up_msp_if_eligible", period.this_year)
        # Apply the SSI exception to the recipient and month, not their unit
        # or every month in a year with some SSI receipt. Do not use general
        # Medicaid eligibility here: it depends on the net Medicare premium.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        return takes_up | receives_ssi
