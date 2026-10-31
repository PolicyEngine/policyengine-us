from policyengine_us.model_api import *


class ct_ssp_own_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP own earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/upms/upm5---treatment-of-income-income-eligibility/5020_05.doc",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/upms/upm5---treatment-of-income-income-eligibility/5020_70.doc",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/upms/upm5---treatment-of-income-income-eligibility/5030_10.doc",
    )
    documentation = (
        "A person's own earned income in a Connecticut AABD budget. UPM "
        "5030.10 A subtracts earned disregards from the assistance unit's "
        "monthly total available gross earned income. For a spouse's income, "
        "UPM 5020.70 C.3.a reduces the deemor's self-employment earnings by "
        "self-employment expenses and C.3.d deems the combined total of the "
        "deemor's gross unearned and applied earned income; UPM 5020.05 A "
        "counts the deemor's income in full except for that chapter's "
        "reductions. No UPM text adopts SSI's income computation or lets a "
        "spouse's residual business loss reduce this person's earnings, so "
        "the SSI offset under POMS SI 00820.210 B.2.c does not apply here. "
        "Own business losses still reduce own wages. The result is floored at "
        "zero: an own residual loss already reduces any earnings deemed from "
        "an ineligible spouse, which use that spouse's after-loss SSI "
        "earnings, so it must not be deducted again."
    )

    def formula(person, period, parameters):
        return max_(person("ssi_earned_income", period), 0)
