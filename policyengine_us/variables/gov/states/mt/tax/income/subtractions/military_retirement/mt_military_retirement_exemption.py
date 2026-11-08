from policyengine_us.model_api import *


class mt_military_retirement_exemption(Variable):
    value_type = float
    entity = Person
    label = "Montana working military retirement and survivor benefit exemption"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Form WMRE computes the exemption for the whole return, so the tax "
        "unit head carries it."
    )
    reference = (
        "https://archive.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://revenue.mt.gov/files/Forms/Montana-Working-Military-Retirement-and-Survivor-Benefit-Exemption.pdf#page=1",
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.subtractions.military_retirement
        tax_unit = person.tax_unit
        filer = person("is_tax_unit_head_or_spouse", period)
        eligible = filer & person("mt_military_retirement_exemption_eligible", period)
        retirement_pay = tax_unit.sum(
            eligible * person("military_retirement_pay", period)
        )
        survivor_benefits = tax_unit.sum(
            eligible * person("military_retirement_pay_survivors", period)
        )
        # 15-30-2120(8): the lesser of the return's Montana source wage
        # income or the rate times the military retirement pay. Form WMRE
        # lines 2 to 5 count wages and the net income of a business, a
        # partnership or S corporation, and a farm, each at least zero.
        earned_income = 0
        for source in [
            "irs_employment_income",
            "self_employment_income",
            "partnership_s_corp_income",
            "farm_income",
        ]:
            earned_income = earned_income + max_(
                0, tax_unit.sum(filer * person(source, period))
            )
        retirement_exemption = min_(p.rate * retirement_pay, earned_income)
        # 15-30-2120(3)(n)(ii): survivor benefits need no earned income.
        survivor_exemption = p.survivor_rate * survivor_benefits
        is_head = person("is_tax_unit_head", period)
        return p.in_effect * is_head * (retirement_exemption + survivor_exemption)
