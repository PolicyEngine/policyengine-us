from policyengine_us.model_api import *


class nm_ctc_qualifying_children(Variable):
    value_type = int
    entity = TaxUnit
    label = "New Mexico child income tax credit qualifying children"
    documentation = """
    Number of qualifying children for the New Mexico child income tax credit.
    NMSA 7-2-18.34(J)(2) adopts the IRC 152(c) qualifying-child definition,
    which has no taxpayer identification number requirement, so a child with
    an ITIN (or no Social Security number) counts here although the federal
    EITC (IRC 32(c)(3)(D)) does not count them. A child who is not disabled
    must also be younger than the filer, or than either spouse on a joint
    return (IRC 152(c)(3)(A)).
    """
    definition_period = YEAR
    reference = (
        # NMSA 7-2-18.34(J)(2) defines "qualifying child" by IRC 152(c).
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503818/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcHYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA",
        "https://www.law.cornell.edu/uscode/text/26/152#c",
        "https://realfile.tax.newmexico.gov/2025pit-rc-ins.pdf#page=10",
        # Publication 596, qualifying child age test: "younger than you (or
        # your spouse if filing jointly)". PDF pages 10, 12.
        "https://www.irs.gov/pub/irs-prior/p596--2025.pdf#page=10",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # NMSA 7-2-18.34(J)(2): "qualifying child" means "qualifying child" as
        # defined by IRC 152(c), and also a minor child or stepchild who would
        # qualify if public assistance toward their support were counted as
        # the taxpayer's. is_eitc_qualifying_child applies the 152(c) tests
        # the model records (relationship, and age or permanent and total
        # disability) and leaves out the EITC identification requirement of
        # IRC 32(c)(3)(D), which 152(c) does not contain. The model does not
        # record the 152(c)(1)(D) own-support test, so every dependent who
        # passes the other tests is treated as meeting it.
        # A filer who can be claimed elsewhere is treated as having no
        # dependents (IRC 152(b)(1)), but 7-2-18.34 counts 152(c) qualifying
        # children rather than dependents, so the count does not drop to zero
        # here; nm_ctc applies the claimant test of 7-2-18.34(A).
        qualifying_child = person("is_eitc_qualifying_child", period)
        # IRC 152(c)(3)(A) also requires the child to be "younger than the
        # taxpayer claiming such individual as a qualifying child"; on a joint
        # return, younger than either spouse (Publication 596). 152(c)(3)(B)
        # treats the requirement as met for a permanently and totally
        # disabled child.
        age = person("age", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        oldest_filer_age = tax_unit.max(where(filer, age, 0))
        younger_than_a_filer = age < tax_unit.project(oldest_filer_age)
        disabled = person("is_permanently_and_totally_disabled", period)
        meets_relative_age_test = younger_than_a_filer | disabled
        return tax_unit.sum(qualifying_child & meets_relative_age_test)
