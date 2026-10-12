from policyengine_us.model_api import *


class vt_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child care and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05828c",
        "https://legislature.vermont.gov/Documents/2022/Docs/ACTS/ACT138/ACT138%20As%20Enacted.pdf#page=3",
        "https://legislature.vermont.gov/Documents/2024/Docs/ACTS/ACT072/ACT072%20As%20Enacted.pdf#page=14",
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112-2022.pdf#page=2",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc
        # The form refers to 2022 Form 2441 line 11, which caps the credit at tax
        # liability. 32 V.S.A. § 5828c sets the credit at 72% of "the federal
        # child and dependent care credit allowed to the taxpayer," and § 5824
        # adopts the federal income tax laws as in effect on December 31, 2024.
        # From 2026 that frozen Code excludes the OBBBA section 21 rate increase,
        # so Vermont uses the pre-OBBBA federal credit.
        if period.start.year >= 2026:
            federal_cdcc = tax_unit("pre_obbba_capped_cdcc", period)
        else:
            federal_cdcc = tax_unit("capped_cdcc", period)
        # 2022 Act 138 raised the 5828c match to 72 percent but retained the
        # low-income adjusted gross income cap and the certified-facility
        # requirement for 2022; 2023 Act 72 removed them effective 2023. We
        # do not track facility certification or in-state care at the moment.
        if p.income_limit_in_effect:
            income_eligible = tax_unit("vt_low_income_cdcc_eligible", period)
            return income_eligible * federal_cdcc * p.rate
        return federal_cdcc * p.rate
