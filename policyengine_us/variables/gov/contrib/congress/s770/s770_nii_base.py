from policyengine_us.model_api import *
from policyengine_us.reforms.congress.s770.section_8 import enabled


class s770_nii_base(Variable):
    value_type = float
    entity = TaxUnit
    label = "S.770 signed NII with selected source adjustments"
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
    documentation = (
        "Existing signed NII, adjusted when the active option applies for "
        "validated NOL denial and items actually subject to FICA/SECA. The "
        "NOL hook changes broadened NII itself before unified allocation, "
        "not a separately floored active bucket. No federal section 172 "
        "deduction is automatically modeled. Literal section 8 also broadens "
        "ordinary-course investment income and business-property gains; "
        "their full classification is unsupported here. Missing passive "
        "pass-through income in unrepaired data understates this NII source "
        "while overstating the active residual; see the reform documentation."
    )

    def formula(tax_unit, period, parameters):
        nii = tax_unit("net_investment_income", period)
        p = parameters(period).gov.contrib.congress.s770.section_8.active_business
        if not enabled(p, period):
            return nii
        overlap = tax_unit_non_dep_add(tax_unit, period, ["s770_passive_se_income"])
        nii = nii - overlap - tax_unit("s770_nii_fica_seca_income", period)
        if p.deny_nol:
            nii = nii + tax_unit("s770_niit_nol_deduction", period)
        return nii
