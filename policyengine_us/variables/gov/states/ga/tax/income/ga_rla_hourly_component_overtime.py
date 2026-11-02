from policyengine_us.model_api import *


class ga_rla_hourly_component_overtime(Variable):
    value_type = float
    entity = Person
    label = "Georgia Railway Labor Act hourly component overtime compensation"
    unit = USD
    documentation = (
        "Annual hourly component overtime compensation, as the applicable "
        "collective bargaining agreement defines it, from an employer governed "
        "by the federal Railway Labor Act, included in employment_income. It "
        "counts only for a full-time employee paid by an hourly wage. "
        "Employers report it in Form W-2, Box 14a, code GA OT, before the "
        "$1,750 limit. The default dataset does not carry it, so "
        "microsimulations on that dataset count none."
    )
    definition_period = YEAR
    defined_for = StateCode.GA
    uprating = "calibration.gov.irs.soi.employment_income"
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080#page=6",
        "https://dor.georgia.gov/document/document/2026-employers-tax-guide-updated-june-2026/download#page=4",
    )
