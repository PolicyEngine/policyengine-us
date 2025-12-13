from policyengine_us.model_api import *


class wi_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Works eligible"
    definition_period = MONTH
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/iii/145",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        demographic = spm_unit("is_demographic_tanf_eligible", period)
        person = spm_unit.members
        is_qualified = person("is_citizen_or_legal_immigrant", period)
        citizenship = spm_unit.any(is_qualified)
        income = spm_unit("wi_works_income_eligible", period)
        resources = spm_unit("wi_works_resources_eligible", period)
        return demographic & citizenship & income & resources
