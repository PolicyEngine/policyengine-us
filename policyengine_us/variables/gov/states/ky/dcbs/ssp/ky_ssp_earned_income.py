from policyengine_us.model_api import *


class ky_ssp_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Kentucky SSP earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        # PDF pages 187-188.
        "https://www.chfs.ky.gov/agencies/dcbs/dfs/Documents/OMVOLIVA.pdf#page=187",
    )
    documentation = (
        "Kentucky SSP own earned income, retaining the existing wage-limited "
        "pretax premium exclusion. 921 KAR 2:015 section 8(1) incorporates "
        "medically needy policy. Volume IVA MS 2450 B.4 measures business "
        "profit; C.7 lists allowable deductions; C.8(b) forbids transferring "
        "a loss between businesses. No Kentucky text authorizes a loss "
        "against other income, so each business is floored at zero: its loss "
        "reduces neither another business's profit nor wages or a spouse's "
        "earnings. This departs from SSI's loss offsets under POMS SI "
        "00820.210 A.2 and B.2.b-c. Inputs may "
        "already aggregate multiple businesses; their separate profits and "
        "Kentucky-specific expense adjustments are not exposed."
    )

    def formula(person, period, parameters):
        sources = parameters(
            period
        ).gov.states.ky.dcbs.ssp.earned.self_employment_sources
        # MS 2450 B.4, C.7 and C.8(b): profit after allowable expenses,
        # without transferring losses to other businesses or other income.
        floored_business_income = [
            max_(person(source, period), 0) for source in sources
        ]
        business_income = sum(floored_business_income)
        wages = max_(person("employment_income", period), 0)
        pretax_premiums = max_(person("pre_tax_health_insurance_premiums", period), 0)
        return wages - min_(wages, pretax_premiums) + business_income
