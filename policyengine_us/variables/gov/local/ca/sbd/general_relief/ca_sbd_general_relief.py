from policyengine_us.model_api import *


class ca_sbd_general_relief(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "San Bernardino County General Relief"
    definition_period = MONTH
    defined_for = "ca_sbd_general_relief_eligible"
    reference = (
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/9e5e1b1a-e577-4f84-92c4-86574a9ff0cf.docx",
        "https://sanbernardino.legistar1.com/sanbernardino/attachments/b2fb756f-da07-452e-bdba-e3c4eda464c5.doc",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=17000.",
    )

    def formula(spm_unit, period, parameters):
        # NOTE: GR benefits are loans repayable to the county; the cash flow
        # is modeled as a benefit and repayment is not modeled. The
        # three-months-of-aid-per-12-month limit for employable recipients is
        # also not modeled, so annualized results can overstate an employable
        # recipient's GR. The homeless full-grant rule (GRPHB HL #7356
        # p. A-7) is a no-op in the flat-grant era, since every eligible unit
        # already receives the full grant for its size.
        grant = spm_unit("ca_sbd_general_relief_maximum_basic_grant", period)
        countable_income = spm_unit("ca_sbd_general_relief_countable_income", period)
        # Countable income is floored at zero so net losses (e.g.,
        # self-employment or rental losses) cannot inflate the grant. No
        # outer floor is needed: defined_for already requires income
        # eligibility, which guarantees countable income below the grant.
        return grant - max_(countable_income, 0)
