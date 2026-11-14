from policyengine_us.model_api import *


class ny_ccap_family_assistance(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York Family Assistance counted for CCAP"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    documentation = (
        "New York's Family Assistance grant (ny_tanf) that the family "
        "takes up. New York counts it as income under 18 NYCRR "
        "404.5(b)(5)(vi), and a family receiving it pays no family share "
        "under 415.3(e)(1). PolicyEngine reads New York's own grant "
        "because the federal TANF aggregate sums other states' programs, "
        "whose dependent care deductions read child care subsidies."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10",
        "https://web.archive.org/web/20240522174244id_/https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=18",
    )

    def formula(spm_unit, period, parameters):
        if parameters(period).gov.hhs.tanf.abolish_tanf:
            return 0
        takes_up = spm_unit("takes_up_tanf_if_eligible", period.this_year)
        return spm_unit("ny_tanf", period) * takes_up
