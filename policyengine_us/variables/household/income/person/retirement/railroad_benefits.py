from policyengine_us.model_api import *


class railroad_benefits(Variable):
    value_type = float
    entity = Person
    label = "Railroad Retirement Board benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Gross annual benefits paid by the Railroad Retirement Board, such as "
        "retirement, disability, spouse and survivor annuities, before Medicare "
        "premiums or other amounts are withheld: the social security "
        "equivalent benefit (Form RRB-1099) plus the rest of the annuity "
        "(Form RRB-1099-R). Railroad Unemployment Insurance Act benefits are "
        "reported elsewhere: unemployment benefits in "
        "unemployment_compensation and sickness benefits in "
        "disability_benefits. Census counts railroad retirement as a "
        "government transfer, and household and SPM benefits include these "
        "benefits. Enter the parts, not this total, so that taxes see them. "
        "A total entered here replaces the sum of the parts and reaches "
        "income totals and benefit programs but no tax, and it applies only "
        "to the year it is entered for, while the parts carry into later "
        "years. Do not also enter them as social_security, pension_income, "
        "disability_benefits or survivor_benefits."
    )
    adds = [
        "railroad_social_security_equivalent_benefits",
        "taxable_railroad_pension_benefits",
        "tax_exempt_railroad_pension_benefits",
    ]
    reference = "https://www2.census.gov/programs-surveys/cps/methodology/Appendix%20A%20P60-200%20income%20measurement%20definition.pdf#page=4"
