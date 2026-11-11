from policyengine_us.model_api import *


class in_homestead_property_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana property tax liability on the qualifying homestead"
    documentation = (
        "Property tax first due and payable for the year on the homestead that "
        "receives the IC 6-1.1-12-37 standard deduction, after the credits "
        "applied before the supplemental homestead credit (including the "
        "Over 65 and Blind/Disabled credits) and before the supplemental "
        "homestead credit. Excludes tax on any other property. By default "
        "this is real_estate_taxes less the Over 65 and Blind/Disabled "
        "property tax credits, the earlier credits the model has, floored at "
        "0; real_estate_taxes stands in for the homestead's tax, as it does "
        "for those credits. Set this to override the default."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    reference = (
        # SEA 1 (2025): SECTION 73 amends IC 6-1.1-20.6-3(3), the liability
        # after all credits, including sections 7 and 7.5 but not 7.7 or 8.5;
        # SECTION 74 adds IC 6-1.1-20.6-7.7(c)(1)(A). PDF pages 123-124
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=123",
        # DLGF June 18, 2025 FAQ, questions 27, 29 and 33 (order of operations)
        # PDF pages 7-9
        "https://www.in.gov/dlgf/files/2025-presentations/250618-FAQ-Webinar-Legislative-Update.pdf#page=7",
    )

    def formula(tax_unit, period, parameters):
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        earlier_credits = add(
            tax_unit,
            period,
            ["in_over_65_property_tax_credit", "in_blind_disabled_property_tax_credit"],
        )
        return max_(property_tax - earlier_credits, 0)
