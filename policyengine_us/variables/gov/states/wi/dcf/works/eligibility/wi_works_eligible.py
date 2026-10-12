from policyengine_us.model_api import *


class wi_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Works eligible"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145",
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/02/2.02.1_List_of_Criteria.htm",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        demographic = spm_unit("is_demographic_tanf_eligible", period)
        person = spm_unit.members
        is_qualified = person("is_citizen_or_legal_immigrant", period.this_year)
        citizenship = spm_unit.any(is_qualified)
        income = spm_unit("wi_works_income_eligible", period)
        resources = spm_unit("wi_works_resources_eligible", period)
        parent = person("is_parent", period.this_year)
        ssi_recipient = (person("ssi", period) > 0) | person(
            "wi_cts_state_only_ssi_recipient", period
        )
        # SSI receipt excludes the applicant, not an otherwise eligible
        # co-parent or a household merely containing a child on SSI.
        all_parents_on_ssi = spm_unit.any(parent & ssi_recipient) & ~spm_unit.any(
            parent & ~ssi_recipient
        )
        return demographic & citizenship & income & resources & ~all_parents_on_ssi
