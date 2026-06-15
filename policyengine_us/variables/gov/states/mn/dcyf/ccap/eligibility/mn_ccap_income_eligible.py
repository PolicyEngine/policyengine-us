from policyengine_us.model_api import *


class mn_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        # Minn. Stat. 142E.06 subd. 1 — income eligibility (formerly 119B.09);
        # DHS-6413N entrance and exit limits.
        "https://www.revisor.mn.gov/statutes/cite/142E.06",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mn.dcyf.ccap.income.smi_rate
        countable_income = spm_unit("mn_ccap_countable_income", period.this_year)
        smi = spm_unit("hhs_smi", period.this_year)
        enrolled = spm_unit("mn_ccap_enrolled", period)
        # Minnesota Family Investment Program / Diversionary Work Program
        # families enter at 67% of SMI; all other families enter at 47%.
        on_mfip_or_dwp = spm_unit("is_tanf_enrolled", period)
        entrance_rate = where(
            on_mfip_or_dwp,
            p.entrance_mfip,
            p.entrance_other,
        )
        # Applicants are tested against the entrance limit; families already
        # enrolled remain eligible until income exceeds 85% of SMI during the
        # 12-month eligibility period.
        smi_rate = where(enrolled, p.exit_during_period, entrance_rate)
        return countable_income <= smi * smi_rate
