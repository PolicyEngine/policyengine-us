from policyengine_us.model_api import *


class co_social_security_subtraction_head(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado social security subtraction for head"
    defined_for = StateCode.CO
    unit = USD
    reference = (
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AD_2022.pdf#page=1",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=12",
        "https://advance.lexis.com/documentpage/?pdmfid=1000516&crid=d0c36b4d-118b-4999-860c-acf7e2abc639&nodeid=ABPAACAACAABAACAAF&nodepath=%2FROOT%2FABP%2FABPAAC%2FABPAACAAC%2FABPAACAACAAB%2FABPAACAACAABAAC%2FABPAACAACAABAACAAF&level=6&haschildren=&populated=false&title=39-22-104.+Income+tax+imposed+on+individuals%2C+estates%2C+and+trusts+-+single+rate+-+report+-+legislative+declaration+-+definitions+-+repeal.&config=014FJAAyNGJkY2Y4Zi1mNjgyLTRkN2YtYmE4OS03NTYzNzYzOTg0OGEKAFBvZENhdGFsb2d592qv2Kywlf8caKqYROP5&pddocfullpath=%2Fshared%2Fdocument%2Fstatutes-legislation%2Furn%3AcontentItem%3A683G-JJ73-CGX8-04HR-00008-00&ecomp=7gf59kk&prid=a3e24fb9-619e-4e55-9f4a-0513857dd3ef"
        # C.R.S. 39-22-104(4)(f)(III)
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.tax.income.subtractions.pension
        person = tax_unit.members
        taxable_social_security = person("taxable_social_security", period)
        social_security_survivors = person("social_security_survivors", period)
        age_head = tax_unit("age_head", period)
        younger_condition = age_head < p.younger.age
        older_condition = age_head >= p.older.age
        head_sss = tax_unit.max(
            social_security_survivors * person("is_tax_unit_head", period)
        )
        head_tss = tax_unit.max(
            taxable_social_security * person("is_tax_unit_head", period)
        )
        older_output = where(
            older_condition, head_tss, min_(head_tss, p.younger.max_amount)
        )

        return where(
            younger_condition,
            head_sss,
            where(older_condition, head_tss, older_output),
        )
