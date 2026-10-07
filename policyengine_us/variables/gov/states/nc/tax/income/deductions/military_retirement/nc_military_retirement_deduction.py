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
        survivor_pay = person("military_retirement_pay_survivors", period)
        # When survivor pay is recorded separately, military_retirement_pay
        # contains the recipient's own retirement pay. A qualifying survivor
        # benefit does not make their own otherwise ineligible pay deductible.
        own_record_eligible = (
            person("years_in_military", period) >= p.minimum_years
        ) | person("is_permanently_disabled_veteran", period)
        # Preserve explicit own-pay eligibility inputs. If eligibility comes
        # from survivor benefits, own pay still needs its own qualifying record.
        own_pay_eligible = eligible & (~survivor | own_record_eligible)
        military_pay_eligible = where(survivor_pay > 0, own_pay_eligible, eligible)
        # With no separate survivor amount, military_retirement_pay can instead
        # contain only survivor benefits, as its documentation permits. Mixed
        # own and survivor pay must be split between the two income inputs.
        qualifying_pay = (
            person("military_retirement_pay", period) * military_pay_eligible
            + survivor_pay * survivor
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(qualifying_pay * head_or_spouse) * p.fraction
