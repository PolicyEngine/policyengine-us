from policyengine_us.model_api import *


class nm_low_income_comprehensive_tax_rebate_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico low income comprehensive tax rebate exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://casetext.com/statute/new-mexico-statutes-1978/chapter-7-taxation/article-2-income-tax-general-provisions/section-7-2-14-low-income-comprehensive-tax-rebate?sort=relevance&type=regulation&tab=keyword&jxs=&resultsNav=false",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        """
        Quoting from N.M. Stat. § 7-2-14(C):
          For the purposes of this section, the total number of exemptions
          for which a tax rebate may be claimed or allowed is determined by
          adding the number of federal exemptions allowable for federal income
          tax purposes for each individual included in the return who is
          domiciled in New Mexico...
        """
        federal_exemptions = tax_unit("exemptions_count", period)
        """
          ...plus two additional exemptions for each individual domiciled
          in New Mexico included in the return who is sixty-five years of
          age or older...
        NB: The tax form shows that this and the blind exemption apply
            only to head and spouse, not dependents.
            https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf#page=58
        """
        p = parameters(
            period
        ).gov.states.nm.tax.income.rebates.low_income.exemptions
        aged_exemptions_head = p.aged.calc(tax_unit("age_head", period))
        aged_exemptions_spouse = p.aged.calc(tax_unit("age_spouse", period))
        """
          ...plus one additional exemption for each individual domiciled
          in New Mexico included in the return who, for federal income tax
          purposes, is blind...
        """
        blind_head_plus_spouse = add(
            tax_unit, period, ["blind_head", "blind_spouse"]
        )
        blind_exemptions = p.blind * blind_head_plus_spouse
        """
          ...plus one exemption for each minor child or stepchild of the
          resident who would be a dependent for federal income tax purposes
          if the public assistance contributing to the support of the child
          or stepchild was considered to have been contributed by the resident.
        NB: This section is not defined in the tax form, so we skip it.
        """
        return (
            federal_exemptions
            + aged_exemptions_head
            + aged_exemptions_spouse
            + blind_exemptions
        )
