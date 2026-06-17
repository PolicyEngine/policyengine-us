from policyengine_us.model_api import *


class nv_ccdp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on income"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Care/CC%20PT%2006-25%20ANNUAL%20INCOME%20CHANGES%2010.02.2025.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.ccdp.income
        # Countable income is YEAR-defined; convert to a monthly figure to
        # compare against the monthly SMI accessor.
        countable_income = (
            spm_unit("nv_ccdp_countable_income", period.this_year) / MONTHS_IN_YEAR
        )
        monthly_smi = spm_unit("nv_ccdp_smi", period)
        enrolled = spm_unit("nv_ccdp_enrolled", period)
        # New applicants must be at or below 41% SMI (intake). Enrolled families
        # are redetermined at or below 49% SMI (renewal); this matches the
        # published renewal income/copay chart (CC PT 06-25), whose copay bands
        # top out at 49% SMI. A separate federal protection (45 CFR
        # 98.21(a)(1)(ii)) bars terminating a family mid-certification until
        # income exceeds 85% SMI, but we don't track certification periods at
        # the moment, so the 85% mid-period ceiling is not modeled.
        income_limit = monthly_smi * where(enrolled, p.smi_renewal, p.smi_intake)
        return countable_income <= income_limit
