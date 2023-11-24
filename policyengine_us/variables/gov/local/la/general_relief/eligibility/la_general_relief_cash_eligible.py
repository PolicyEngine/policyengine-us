from policyengine_us.model_api import *


class la_general_relief_cash_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Los Angeles County General Relief based on the cash requirements"
    # Person has to be a resident of LA County
    defined_for = "in_la"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        cash = spm_unit("spm_unit_cash_assets", period)
        married = add(spm_unit, period, ["is_married"])
        p = parameters(
            period
        ).gov.local.la.general_relief.eligibility.limit.cash
        applicant_eligible = where(
            married, cash <= p.applicant.married, cash <= p.applicant.single
        )
        # Recipients of the GR have an increased cash value limit
        recipient = spm_unit("la_general_relief_recipient", period)
        recipient_eligible = cash <= p.recipient
        return where(recipient, recipient_eligible, applicant_eligible)
