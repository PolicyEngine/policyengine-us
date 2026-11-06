from policyengine_us.model_api import *


class md_famli_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Maryland FAMLI taxable wages"
    documentation = (
        "Wages subject to Maryland Family and Medical Leave Insurance "
        "contributions: Maryland unemployment insurance wages, capped at the "
        "Social Security wage base. Those wages include 401(k) deferrals and "
        "exclude cafeteria plan and dependent care benefits, as "
        "payroll_tax_gross_wages does. Household state proxies work state, "
        "and one person's wages proxy the cap that applies separately to each "
        "job."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gle&section=8.3-601&enactments=false",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gle&section=8.3-101&enactments=false",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gle&section=8-101&enactments=false",
        "https://regs.maryland.gov/us/md/exec/comar/09.42.02.04",
        "https://regs.maryland.gov/us/md/exec/comar/09.32.01.14",
        "https://labor.maryland.gov/employment/empguide/empguide.pdf#page=19",
    )

    def formula(person, period, parameters):
        return min_(
            person("payroll_tax_gross_wages", period),
            parameters(period).gov.irs.payroll.social_security.cap,
        )


class employer_total_md_famli_taxable_wages(Variable):
    value_type = float
    entity = Person
    label = "Employer total Maryland FAMLI taxable wages"
    documentation = (
        "Aggregate employer wages subject to Maryland Family and Medical "
        "Leave Insurance contributions for employer-only payroll tax "
        "calculations."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD

    def formula(person, period, parameters):
        return person("employer_total_taxable_earnings_for_social_security", period)
