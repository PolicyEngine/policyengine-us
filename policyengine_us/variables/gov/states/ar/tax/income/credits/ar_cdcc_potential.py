from policyengine_us.model_api import *


class ar_cdcc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas Child and Dependent Care Credit"
    unit = USD
    reference = (
        "https://codes.findlaw.com/ar/title-26-taxation/ar-code-sect-26-51-502/",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR2441_Child_andDependentCareExpenses.pdf#page=1",
    )
    definition_period = YEAR
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ar.tax.income.credits.cdcc
        # Ark. Code Ann. § 26-51-502(b)(2) matches 20 percent of the federal
        # credit allowable under IRC § 21; Form AR2441 computes that credit
        # without the federal tax liability limitation, so the pre-cap
        # amount applies. The separate refundable credit under
        # § 26-51-502(c) for care at a Department of Education-approved
        # early childhood facility is not modeled; we don't track facility
        # approval at the moment.
        # Arkansas's static conformity to the January 2, 2013 IRC excludes
        # both ARPA's 2021 expansion and the scheduled 2026 federal CDCC
        # change, so from 2021 onward the credit uses the pinned 2013-law
        # replica. Before 2021 the live federal CDCC equals the 2013 law, so
        # cdcc_potential (pre-liability-cap) is used directly.
        if period.start.year >= 2021:
            federal_credit = tax_unit("ar_federal_cdcc", period)
        else:
            federal_credit = tax_unit("cdcc_potential", period)
        return federal_credit * p.match
