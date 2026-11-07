from policyengine_us.model_api import *


class taxable_railroad_pension_benefits(Variable):
    value_type = float
    entity = Person
    label = "Taxable Railroad Retirement pension benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Railroad Retirement Act benefits other than the social security "
        "equivalent benefit, less the employee contributions recovered tax "
        "free: the non-social security equivalent part of tier 1, tier 2, "
        "vested dual benefits and supplemental annuities reported on Form "
        "RRB-1099-R. IRC 72(r)(1) treats these benefits as paid from a "
        "section 401(a) employer plan, so the taxable part is gross income "
        "like any other pension. 45 U.S.C. 231m(a) bars states from taxing "
        "them."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/72#r",
        "https://www.law.cornell.edu/uscode/text/45/231m#a",
        # IRS Pub. 575 (2024): the second category of railroad retirement
        # benefits and the Form RRB-1099-R boxes. PDF pages 7-8.
        "https://www.irs.gov/pub/irs-prior/p575--2024.pdf#page=7",
    )
