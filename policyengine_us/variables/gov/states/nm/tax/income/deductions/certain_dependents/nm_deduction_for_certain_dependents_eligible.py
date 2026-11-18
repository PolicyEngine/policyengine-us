from policyengine_us.model_api import *


class nm_deduction_for_certain_dependents_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligibility for New Mexico deduction for certain dependents"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503892/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcATgBMASgA0ybKUIQAiokK4AntADkW6REJhcCFWs069BoyADKeUgCFNAJQCiAGRcA1AIIA5AMIu0qRgAEbQpOySkkA",
        "https://realfile.tax.newmexico.gov/2025pit-rc-ins.pdf#page=2",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # The deduction uses the same "not a dependent of another individual"
        # test as the rebates and credits on Schedule PIT-RC, and the law does
        # not settle a joint return where only one spouse is a dependent. We
        # apply the PIT-RC instructions' reading, which lets a spouse who is
        # not a dependent still qualify, so only a return on which every
        # filer is a dependent elsewhere is barred.
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        # deduction does not apply if an exemption under IRS 151 is claimed;
        # IRC 151 refers to the federal personal exemption
        federal_exemption_amount = tax_unit("exemptions", period)
        return ~every_filer_dependent & (federal_exemption_amount == 0)
