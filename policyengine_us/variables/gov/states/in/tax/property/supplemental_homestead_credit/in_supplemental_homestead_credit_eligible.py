from policyengine_us.model_api import *


class in_supplemental_homestead_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Qualifies for the Indiana supplemental homestead credit"
    documentation = (
        "Whether the filer qualifies for the homestead standard deduction under "
        "IC 6-1.1-12-37 for their homestead, or is married at the time of death "
        "to a deceased spouse who qualified for it, for the year the property "
        "taxes are first due and payable. The credit needs no application "
        "(IC 6-1.1-20.6-7.7(e)). By default a filer with real_estate_taxes "
        "qualifies, the homeowner proxy the Over 65 credit uses; the model "
        "has no input for the standard deduction itself. Set this to override "
        "the default, for example for property taxes on property that is not "
        "the filer's homestead."
    )
    definition_period = YEAR
    defined_for = StateCode.IN
    reference = (
        # IC 6-1.1-20.6-7.7(b) and (e), added by SEA 1 (2025), SECTION 74
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=124",
        # DLGF June 18, 2025 FAQ, questions 26 and 28
        "https://www.in.gov/dlgf/files/2025-presentations/250618-FAQ-Webinar-Legislative-Update.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["real_estate_taxes"]) > 0
