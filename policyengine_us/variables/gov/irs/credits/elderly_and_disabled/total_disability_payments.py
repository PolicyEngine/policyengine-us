from policyengine_us.model_api import *


class total_disability_payments(Variable):
    value_type = float
    entity = Person
    label = "Disability (total) payments"
    unit = USD
    documentation = (
        "Wages (or payments in lieu thereof) paid to an individual for permanent "
        "and total disability. Defaults to the taxable disability benefits of "
        "someone who retired on permanent and total disability: benefits from "
        "an employer's accident or health plan or pension plan, included in "
        "income as wages or payments instead of wages (IRC 22(c)(2)(B)(iii)). "
        "Amounts received after the employer's mandatory retirement age are not "
        "disability income; the model does not track that age."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/22#c_2_B_iii",
        "https://www.irs.gov/pub/irs-prior/i1040sr--2024.pdf#page=3",
    )

    def formula(person, period, parameters):
        retired_on_total_disability = person("retired_on_total_disability", period)
        taxable_disability_benefits = person("taxable_disability_benefits", period)
        return retired_on_total_disability * taxable_disability_benefits
