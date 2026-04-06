from policyengine_us.model_api import *


class pr_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico adjusted gross income person level"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = (
        "https://hacienda.pr.gov/sites/default/files/individuals_2024_rev._jul_12_24_9-30-24_informative.pdf#page=2",
        "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30103/",
    )

    def formula(person, period, parameters):
        filing_status = person.tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        agi_taxunit = person.tax_unit("pr_agi", period)
        frac = where(filing_status == filing_statuses.JOINT, 0.5, 1.0)
        return agi_taxunit * frac
