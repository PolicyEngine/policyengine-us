from policyengine_us.model_api import *


class ca_riv_share_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Riverside County Sharing Households Assist Riverside's Energy program (SHARE)"
    definition_period = MONTH
    defined_for = "in_riv"
    reference = (
        "https://riversideca.gov/utilities/residents/assistance-programs/share-english"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.cap.share
        countable_income = spm_unit("ca_riv_share_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.income_limit
        # The RPU utility bill must be in the applicant's name.
        # tenant_pays_utilities approximates this; the model cannot identify
        # sub-metered tenants, whose bill is not in their name.
        pays_utilities = spm_unit.household("tenant_pays_utilities", period.this_year)
        return (countable_income <= income_limit) & pays_utilities
