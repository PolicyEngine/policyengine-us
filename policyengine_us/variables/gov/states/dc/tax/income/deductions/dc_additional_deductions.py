from policyengine_us.model_api import *


class dc_additional_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC additional deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        # D.C. Act 26-416, sec. 7112(e): new D.C. Code 47-1803.04(e)(3) to (6).
        "https://code.dccouncil.gov/us/dc/council/acts/26-416",
    )
    defined_for = StateCode.DC
    documentation = (
        "The federal deductions for qualified tips (IRC 224), qualified "
        "overtime compensation (IRC 225), personal car loan interest (IRC "
        "163(h)(4)) and the enhanced senior deduction (IRC 151(d)(5)(C)), "
        "which D.C. Code 47-1803.04(e) allows from 2026 in the amounts allowed "
        "on the federal return. Subsection (e) allows them in computing the "
        "net income of any individual, so they apply with either the standard "
        "deduction or itemized deductions."
    )
    adds = "gov.states.dc.tax.income.deductions.additional.sources"
