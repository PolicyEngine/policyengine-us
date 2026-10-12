from policyengine_us.model_api import *


class ne_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska military retirement subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # Neb. Rev. Stat. 77-2716(15): excludes military retirement benefit
        # income to the extent included in federal AGI.
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-2716",
        # 2025 Form 1040N Schedule I, line 32.
        "https://revenue.nebraska.gov/sites/default/files/doc/tax-forms/2025/f_Individual_Income_Tax_Booklet.pdf#page=26",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.tax.income.agi.subtractions.military_retirement
        person = tax_unit.members
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        military_retirement_benefit = person("military_retirement_pay", period)
        # Dependents' income is not in federal AGI; they report it on their
        # own return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        qualifying_military_retirement_benefits = tax_unit.sum(
            military_retirement_benefit * age_eligible * head_or_spouse
        )
        # From 2015 to 2021, the tax filer may elect to exclude 40% of the military retirement benefit income for 7 consecutive years or elect to receive 15% exclusion for all tax years after age 67.
        return qualifying_military_retirement_benefits * p.fraction
