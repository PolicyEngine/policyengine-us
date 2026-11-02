from policyengine_us.model_api import *


class nv_liheap_fac_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP Fixed Annual Credit income"
    documentation = (
        "Annual gross income used for the Fixed Annual Credit and its benefit "
        "cap band: eligibility income plus TANF and the earnings of "
        "school-attending children."
    )
    defined_for = StateCode.NV
    reference = (
        # PDF pages 43, 46-47, 57, 60
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=43",
        # PDF pages 43, 46-47, 57, 60
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=43",
    )

    def formula(spm_unit, period, parameters):
        child_earnings = add(spm_unit, period, ["nv_liheap_child_earned_income"])
        eligibility_income = spm_unit("nv_liheap_countable_income", period)
        # TANF is counted once at the SPM unit level through the
        # take-up-gated tanf total. The other Fixed Annual Credit-only income
        # types have no inputs.
        # Section 707 M adds the two most recent quarters of earnings to
        # unemployment benefits for the Fixed Annual Credit; quarterly
        # earnings have no input.
        tanf = spm_unit("tanf", period)
        return eligibility_income + child_earnings + tanf
