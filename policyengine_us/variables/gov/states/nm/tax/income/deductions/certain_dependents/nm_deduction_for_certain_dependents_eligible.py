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
        # test as the rebates and credits on Schedule PIT-RC, whose
        # instructions let a spouse who is not a dependent still qualify. So
        # only a return on which every filer is a dependent elsewhere is
        # barred.
        independent_filer = (
            tax_unit("head_spouse_count_not_dependent_elsewhere", period) > 0
        )
        # deduction does not apply if an exemption under IRS 151 is claimed;
        # IRC 151 refers to the federal personal exemption
        federal_exemption_amount = tax_unit("exemptions", period)
        return independent_filer & (federal_exemption_amount == 0)
