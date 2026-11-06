from policyengine_us.model_api import *


class nj_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey adjusted gross income"
    documentation = (
        "New Jersey adjusted gross income of the head and spouse. A tax unit "
        "dependent's income belongs on the dependent's own New Jersey return, "
        "so it is left out."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54/section-54-8a-36/",
        # N.J.S.A. 54A:8-3.1(a): each individual over the gross income
        # threshold files a return; (b): only a husband and wife file a
        # joint return; (f): a minor's return is filed by a fiduciary.
        "https://codes.findlaw.com/nj/title-54a-new-jersey-gross-income-tax-act/nj-st-sect-54a-8-3-1/",
        # 2025 NJ-1040 instructions, PDF pages 5, 40: who must file, with no
        # exception for dependents, and Worksheet L ("dependents who do not
        # file a New Jersey tax return")
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=5",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # A dependent's income goes on the dependent's own return.
        total_income = tax_unit_non_dep_add(tax_unit, period, ["nj_total_income"])
        p = parameters(period).gov.states.nj.tax.income
        exclusions = add(tax_unit, period, p.all_exclusions)
        return max_(0, total_income - exclusions)
