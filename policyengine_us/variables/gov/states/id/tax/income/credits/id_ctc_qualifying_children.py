from policyengine_us.model_api import *


class id_ctc_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "Idaho Child Tax Credit qualifying children"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3029L/",
        # 2025 Idaho Form 40 instructions, Line 24 Idaho Child Tax Credit
        # Worksheet.
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.credits.ctc
        person = tax_unit.members
        # Idaho Code 63-3029L(1): "the term "qualifying child" has the meaning
        # as defined in section 24(c) of the Internal Revenue Code." Idaho
        # does not require the federal credit to be allowed, so a child whose
        # filer fails the federal identification requirements of IRC 24(e)(2)
        # or 24(h)(7)(A)(i) still counts. The Form 40 instructions list only
        # "Your qualifying child" and "Age 16 or under". The model still
        # applies the federal child social security number rule (IRC
        # 24(h)(7)(A)(ii)) and the IRC 152(b)(1) dependent-filer rule here.
        qualifying_child = person(
            "ctc_qualifying_child_ignoring_filer_identification", period
        )
        # IRC 24(c) defines eligible children under the federal CTC. Its age
        # test is under 17; the 2021 federal expansion to age 17 is in IRC
        # 24(i)(1), so Idaho does not count those children in 2021.
        age_eligible = person("age", period) < p.ineligible_age
        return tax_unit.sum(qualifying_child & age_eligible)
