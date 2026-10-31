from policyengine_us.model_api import *


class ri_military_retirement_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Rhode Island military service pension subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.RI
    reference = (
        # R.I. Gen. Laws 44-30-12(c)(11); the Division of Taxation's
        # interpretation extends the exemption to surviving spouses.
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-II/44-30-12.htm",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2024-03/PUB_2024-01_retirement_income_guide.pdf#page=16",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-01/PUB_2025-01_Retirement_Income_Guide.pdf#page=17",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2026-02/PUB_2026-01_Retirement_Income_Guide.pdf#page=15",
    )

    def formula_2023_01_01(person, period, parameters):
        retirement_pay = person("military_retirement_pay", period)
        survivor_pay = person("military_retirement_pay_survivors", period)
        surviving_spouse = person("is_surviving_spouse", period)
        return retirement_pay + survivor_pay * surviving_spouse
