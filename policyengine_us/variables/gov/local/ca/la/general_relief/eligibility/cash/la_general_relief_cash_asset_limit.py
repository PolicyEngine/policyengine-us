from policyengine_us.model_api import *


class la_general_relief_cash_asset_limit(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Limit for the Los Angeles County General Relief cash asset requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(
            period
        ).gov.local.ca.la.general_relief.eligibility.limit.cash
        applicant_limit = where(
            married, p.applicant.married, p.applicant.single
        )
        # Recipients of the GR have an increased cash value limit
        recipient = spm_unit("la_general_relief_recipient", period)
        return where(recipient, p.recipient, applicant_limit)
