from policyengine_us.model_api import *


class pr_gross_income_person(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico gross income person"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1005-computation-of-taxable-income/subchapter-a-determination-of-net-income-general-concepts/30101-gross-income"
