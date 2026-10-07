from policyengine_us.model_api import *


class nc_military_retirement_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina military retirement deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "nc_military_retirement_deduction_eligible"
    reference = (
        "https://www.ncdor.gov/2022-d-401-individual-income-tax-instructions/open#page=18",
        "https://law.justia.com/codes/north-carolina/chapter-105/article-4/section-105-153-5/",
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/filing-topics/military-retirement",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nc.tax.income.deductions.military_retirement
        # G.S. 105-153.5(b) allows only items included in the taxpayer's
        # adjusted gross income, which leaves out dependents' income (they
        # file their own return). Eligibility is each recipient's own:
        # (5a)a. covers the retirement pay of a retired member who meets the
        # service or medical-retirement test, and (5a)b. Survivor Benefit Plan
        # payments to the beneficiary of such a member.
        person = tax_unit.members
        eligible = person("nc_military_retirement_deduction_eligible", period)
        survivor = person("nc_military_retirement_survivor_eligible", period)
        # military_retirement_pay includes survivor benefits; some survivor
        # benefits are recorded separately as military_retirement_pay_survivors.
        qualifying_pay = person("military_retirement_pay", period) * eligible + (
            person("military_retirement_pay_survivors", period) * survivor
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(qualifying_pay * head_or_spouse) * p.fraction
