from policyengine_us.model_api import *


class pa_taxable_elective_deferrals(Variable):
    value_type = float
    entity = Person
    label = "Elective deferrals taxable by PA but not by US"
    unit = USD
    documentation = (
        "Traditional 401(k) and 403(b) elective deferrals that federal wages "
        "leave out but Pennsylvania taxes as compensation. An employee's own "
        "contributions to an employer retirement plan, whether by payroll "
        "deduction or salary reduction, are not excludable from Pennsylvania "
        "compensation."
    )
    definition_period = YEAR
    reference = (
        # 2025 PA-40 IN, Line 1a: "The contributions you make to your
        # employer's sponsored retirement plan are PA-taxable compensation".
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40in.pdf#page=12",
        # 61 Pa. Code 101.6(c)(8)(ii)(B).
        "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/061/chapter101/s101.6.html",
        # PA PIT Guide, Gross Compensation: employee contributions taxable.
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/papersonalincometaxguide/documents/pitguide_grosscompensation.pdf#page=51",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.tax.income
        deferrals = add(person, period, p.taxable_elective_deferral_sources)
        # Federal wages are floored at zero, so they leave out the deferrals
        # only up to the wages themselves. Add back no more than that.
        employment_income = person("employment_income", period)
        federal_wages = person("irs_employment_income", period)
        return min_(deferrals, employment_income - federal_wages)
