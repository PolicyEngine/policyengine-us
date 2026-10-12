from policyengine_us.model_api import *


class vt_nonrefundable_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont nonrefundable child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2021/title-32/chapter-151/section-5822/",
        "https://legislature.vermont.gov/Documents/2022/Docs/ACTS/ACT138/ACT138%20As%20Enacted.pdf#page=2",
    )
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.credits.cdcc
        federal_cdcc = tax_unit("capped_cdcc", period)
        # 32 V.S.A. § 5822(d)(1) matched 24 percent of the federal credit
        # through 2021; 2022 Act 138 struck the child and dependent care
        # leg. The § 5828c low-income credit is claimed in lieu of this
        # credit, and a low-income filer always prefers its larger
        # refundable match, so income-eligible filers are excluded. We
        # assume care at a facility qualifying for the § 5828c credit.
        low_income_eligible = tax_unit("vt_low_income_cdcc_eligible", period)
        return ~low_income_eligible * federal_cdcc * p.nonrefundable.rate
