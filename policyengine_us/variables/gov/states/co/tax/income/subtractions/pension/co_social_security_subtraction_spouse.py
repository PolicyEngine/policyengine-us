from policyengine_us.model_api import *


class co_social_security_subtraction_spouse(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado social security subtraction for spouse"
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
        age_spouse = tax_unit("age_spouse", period)
        younger_condition = age_spouse < p.younger.age
        older_condition = age_spouse >= p.older.age
        spouse_sss = tax_unit.max(
            social_security_survivors * person("is_tax_unit_spouse", period)
        )
        spouse_tss = tax_unit.max(
            taxable_social_security * person("is_tax_unit_spouse", period)
        )
        cap_older_amount = min_(spouse_tss, p.younger.max_amount)
        older_output = where(older_condition, spouse_tss, cap_older_amount)
        older_allowable = where(older_condition, spouse_tss, older_output)
        return where(
            younger_condition,
            spouse_sss,
            older_allowable,
        )
