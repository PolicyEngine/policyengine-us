from policyengine_us.model_api import *


class md_employer_famli_contribution(Variable):
    value_type = float
    entity = Person
    label = "Maryland employer FAMLI contribution"
    documentation = (
        "Employer-side Maryland Family and Medical Leave Insurance "
        "contribution, owed only by employers of 15 or more employees. This "
        "uses one annual employer_headcount for the size test, which Maryland "
        "applies quarterly in 2027 and from an annual average after that "
        "(COMAR 09.42.02.06), and it assumes the employer pays only its own "
        "share."
    )
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gle&section=8.3-601&enactments=false",
        "https://regs.maryland.gov/us/md/exec/comar/09.42.02.06",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.tax.payroll.famli
        liable = person("employer_headcount", period) >= p.employer_headcount_threshold
        taxable_wages = person("md_famli_taxable_wages", period)
        return where(liable, p.total_rate * (1 - p.employee_share) * taxable_wages, 0)
