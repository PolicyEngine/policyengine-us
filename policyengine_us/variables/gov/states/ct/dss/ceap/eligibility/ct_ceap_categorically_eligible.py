from policyengine_us.model_api import *


class ct_ceap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Categorically eligible for Connecticut CEAP"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=6,7,11"

    def formula(spm_unit, period, parameters):
        # Positive annual receipt approximates receipt at application.
        # Refugee Cash Assistance and means-tested VA receipt are unavailable;
        # generic veterans_benefits does not establish VA eligibility.
        person = spm_unit.members
        member = ~person("is_in_foster_care", period.first_month)
        ssi = spm_unit.sum(member * person("ssi", period, options=[ADD]))
        # Remove SSP attributable to excluded foster members from the
        # household receipt, preserving a supplied household SSP total.
        excluded_ssp = spm_unit.sum(
            ~member * person("ct_ssp_person", period, options=[ADD])
        )
        ssp = max_(spm_unit("ct_ssp", period, options=[ADD]) - excluded_ssp, 0)
        receipt = add(spm_unit, period, ["snap", "ct_tfa"]) + ssi + ssp > 0
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        return receipt & ~heat_in_rent
