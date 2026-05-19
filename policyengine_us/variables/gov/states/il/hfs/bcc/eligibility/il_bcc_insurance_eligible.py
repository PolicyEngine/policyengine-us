from policyengine_us.model_api import *


class il_bcc_insurance_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Illinois BCC insurance eligible"
    definition_period = YEAR
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=33528",
        "https://www.ilga.gov/legislation/ilcs/documents/030500050K5-2.htm",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Per PM 06-20-02, persons are eligible if they are "uninsured".
        # A person is NOT uninsured (thus ineligible) if they have:
        # - Medicaid eligibility through another pathway
        # - Health coverage that would pay for cancer treatment
        #
        # Exceptions that still qualify as "uninsured":
        # - Coverage with limited benefits
        # - Coverage where lifetime cap has been met/exceeded
        # - Coverage that excludes cancer treatment
        # - Indian Health Service coverage only
        on_medicaid = person("receives_medicaid", period)
        has_qualifying_coverage = person("has_bcc_qualifying_coverage", period)
        has_disqualifying_coverage = on_medicaid | has_qualifying_coverage
        return ~has_disqualifying_coverage
