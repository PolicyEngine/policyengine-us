from policyengine_us.model_api import *


class is_ssi_recipient_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "SSI recipients"
    documentation = (
        "Qualifies for Medicaid due to receiving SSI in Section 1634 and "
        "SSI-criteria states. Section 209(b) states are not blanket-covered "
        "because they may apply criteria that are more restrictive than SSI."
    )
    definition_period = YEAR
    reference = (
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010",
        "https://www.law.cornell.edu/uscode/text/42/1396a#f",
    )

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        categories = parameters(period).gov.hhs.medicaid.eligibility.categories
        is_covered = categories.ssi_recipient.is_covered[state].astype(bool)
        classified = person("medicaid_ssi_recipient_state_classification", period)
        classifications = classified.possible_values
        covered_classification = (classified == classifications.SECTION_1634) | (
            classified == classifications.SSI_CRITERIA
        )
        receives_ssi = person("ssi", period) > 0
        return receives_ssi & is_covered & covered_classification
