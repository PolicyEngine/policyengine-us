from policyengine_us.model_api import *


class mi_ccap_income_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Michigan CDC income-waived eligibility group"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=15"
    )

    def formula(spm_unit, period, parameters):
        # BEM 703 p.15-16: five groups qualify without an income test and have
        # their family contribution waived. We model Children's Protective
        # Services, Foster Care, FIP/SSI-related, and Homeless. The migrant
        # farmworker group is not modeled at the moment (no migrant status is
        # tracked).
        # CPS: open Children's Protective Services case.
        protective_services = (
            add(spm_unit, period, ["receives_or_needs_protective_services"]) > 0
        )
        # Foster Care: active MDHHS foster care case for the child.
        foster_care = add(spm_unit, period, ["is_in_foster_care"]) > 0
        # FIP-related: child or P/SP receives FIP or SSI. MI FIP is TANF; we
        # use is_tanf_enrolled (not computed FIP eligibility) to break the
        # CCAP-TANF circular dependency.
        receives_ssi = (add(spm_unit, period, ["ssi"]) > 0) | (
            add(spm_unit, period, ["receives_ssi"]) > 0
        )
        fip_related = spm_unit("is_tanf_enrolled", period) | receives_ssi
        # Homeless under the McKinney-Vento Act (self-attested).
        homeless = spm_unit.household("is_homeless", period.this_year)
        return protective_services | foster_care | fip_related | homeless
