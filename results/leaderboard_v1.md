# varbench leaderboard

## Headline

| Model | Score | Pass rate | Mean iters | Input tokens | Output tokens |
|---|---|---|---|---|---|
| Claude Sonnet 4.5 | 39/64 | 60.9% | 4.1 | 529110 | 85653 |
| Qwen 2.5 7B (local) | 39/64 | 60.9% | 7.4 | - | - |

## By category

| Category | Claude Sonnet 4.5 | Qwen 2.5 7B (local) |
|---|---|---|
| clinical_interpretation | 27/52 | 35/52 |
| drug_moa | 4/4 | 2/4 |
| population_genetics | 1/1 | 1/1 |
| variant_calling | 1/1 | 0/1 |
| variant_filtering | 4/4 | 1/4 |
| vcf_qc | 2/2 | 0/2 |

## Per-eval results

| eval_id | Claude Sonnet 4.5 | Qwen 2.5 7B (local) |
|---|---|---|
| `ci_clinvar_001_MLH1_89608` | ✅ | ✅ |
| `ci_clinvar_002_MSH2_90638` | ❌ | ✅ |
| `ci_clinvar_003_MLH1_89672` | ✅ | ❌ |
| `ci_clinvar_004_MLH1_90041` | ✅ | ✅ |
| `ci_clinvar_005_GAA_1327504` | ✅ | ✅ |
| `ci_clinvar_006_BRCA1_54782` | ✅ | ✅ |
| `ci_clinvar_007_BRCA1_17693` | ✅ | ✅ |
| `ci_clinvar_008_RAF1_40613` | ✅ | ✅ |
| `ci_clinvar_009_BRCA2_52203` | ✅ | ✅ |
| `ci_clinvar_010_BRCA2_51061` | ✅ | ✅ |
| `ci_clinvar_011_PIK3CD_1406866` | ❌ | ✅ |
| `ci_clinvar_012_PMS2_91307` | ❌ | ✅ |
| `ci_clinvar_013_RUNX1_561243` | ❌ | ❌ |
| `ci_clinvar_014_GP1BB_3775056` | ❌ | ✅ |
| `ci_clinvar_015_F8_368117` | ✅ | ❌ |
| `ci_clinvar_016_HNF1A_435424` | ❌ | ❌ |
| `ci_clinvar_017_PAH_102628` | ❌ | ✅ |
| `ci_clinvar_018_LDLR_251537` | ❌ | ✅ |
| `ci_clinvar_019_DCLRE1C_4851281` | ✅ | ✅ |
| `ci_clinvar_020_PAH_102782` | ❌ | ✅ |
| `ci_clinvar_021_RYR1_590556` | ✅ | ✅ |
| `ci_clinvar_022_HNF4A_3358877` | ❌ | ❌ |
| `ci_clinvar_023_MSH2_90685` | ❌ | ✅ |
| `ci_clinvar_024_RYR1_1210315` | ❌ | ❌ |
| `ci_clinvar_025_SERPINC1_2295171` | ✅ | ✅ |
| `ci_clinvar_026_GAA_499380` | ❌ | ❌ |
| `ci_clinvar_027_LDLR_183125` | ❌ | ✅ |
| `ci_clinvar_028_RUNX1_3336848` | ✅ | ✅ |
| `ci_clinvar_029_GCK_2691834` | ✅ | ✅ |
| `ci_clinvar_030_HNF4A_931741` | ❌ | ✅ |
| `ci_clinvar_031_UBE3A_386114` | ❌ | ❌ |
| `ci_clinvar_032_BRCA2_232126` | ✅ | ✅ |
| `ci_clinvar_033_BRCA1_427350` | ✅ | ✅ |
| `ci_clinvar_034_BRCA2_215603` | ✅ | ❌ |
| `ci_clinvar_035_KRAS_45119` | ✅ | ✅ |
| `ci_clinvar_036_BRCA1_427301` | ✅ | ❌ |
| `ci_clinvar_037_MSH2_91006` | ❌ | ❌ |
| `ci_clinvar_038_BRCA2_427540` | ✅ | ❌ |
| `ci_clinvar_039_RUNX1_3791501` | ✅ | ❌ |
| `ci_clinvar_040_BRCA2_427415` | ✅ | ✅ |
| `ci_clinvar_041_BRCA2_209738` | ✅ | ❌ |
| `ci_clinvar_042_BRCA2_209627` | ❌ | ✅ |
| `ci_clinvar_043_MYH7_164334` | ❌ | ❌ |
| `ci_clinvar_044_RPE65_98867` | ❌ | ✅ |
| `ci_clinvar_045_BRCA2_209635` | ❌ | ✅ |
| `ci_clinvar_046_BRCA1_55314` | ❌ | ✅ |
| `ci_clinvar_047_BRCA1_125746` | ❌ | ❌ |
| `ci_clinvar_048_SLC9A6_139206` | ❌ | ❌ |
| `ci_clinvar_049_RUNX1_339817` | ✅ | ✅ |
| `ci_clinvar_050_PMS2_91284` | ❌ | ✅ |
| `clinical_interpretation_001_brca1_known_pathogenic` | ✅ | ✅ |
| `clinical_interpretation_002_vus_conflicting_evidence` | ✅ | ✅ |
| `drug_moa_001_pcsk9_lof_supports_inhibitor` | ✅ | ✅ |
| `drug_moa_002_cetp_genetics_unclear` | ✅ | ❌ |
| `drug_moa_003_cetp_neutral_evidence` | ✅ | ❌ |
| `drug_moa_004_pcsk9_with_noise` | ✅ | ✅ |
| `population_genetics_001_pcsk9_r46l_ba1_check` | ✅ | ✅ |
| `variant_calling_001_list_heterozygous_variants` | ✅ | ❌ |
| `variant_filtering_001_pass_and_dp30` | ✅ | ❌ |
| `variant_filtering_002_high_impact_consequences` | ✅ | ✅ |
| `variant_filtering_003_multi_condition` | ✅ | ❌ |
| `variant_filtering_004_missense_combined_annotations` | ✅ | ❌ |
| `vcf_qc_001_count_pass_variants` | ✅ | ❌ |
| `vcf_qc_002_titv_ratio` | ✅ | ❌ |

## Failure details

### Claude Sonnet 4.5

- **`ci_clinvar_002_MSH2_90638`**
  - expected: `'Pathogenic'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Pathogenic', got 'Uncertain_significance'
- **`ci_clinvar_011_PIK3CD_1406866`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Likely_pathogenic', got 'Uncertain_significance'
- **`ci_clinvar_012_PMS2_91307`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_013_RUNX1_561243`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_014_GP1BB_3775056`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Likely_pathogenic', got 'Uncertain_significance'
- **`ci_clinvar_016_HNF1A_435424`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_017_PAH_102628`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_018_LDLR_251537`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_020_PAH_102782`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_022_HNF4A_3358877`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_023_MSH2_90685`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_024_RYR1_1210315`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Pathogenic'
- **`ci_clinvar_026_GAA_499380`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_027_LDLR_183125`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_030_HNF4A_931741`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_031_UBE3A_386114`**
  - expected: `'Likely_benign'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Likely_benign', got 'Uncertain_significance'
- **`ci_clinvar_037_MSH2_91006`**
  - expected: `'Likely_benign'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Likely_benign', got 'Likely_pathogenic'
- **`ci_clinvar_042_BRCA2_209627`**
  - expected: `'Benign'`
  - actual:   `'Likely_benign'`
  - reason:   expected 'Benign', got 'Likely_benign'
- **`ci_clinvar_043_MYH7_164334`**
  - expected: `'Benign'`
  - actual:   `'Likely_benign'`
  - reason:   expected 'Benign', got 'Likely_benign'
- **`ci_clinvar_044_RPE65_98867`**
  - expected: `'Benign'`
  - actual:   `'Likely_benign'`
  - reason:   expected 'Benign', got 'Likely_benign'
- **`ci_clinvar_045_BRCA2_209635`**
  - expected: `'Benign'`
  - actual:   `'Likely_benign'`
  - reason:   expected 'Benign', got 'Likely_benign'
- **`ci_clinvar_046_BRCA1_55314`**
  - expected: `'Benign'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Benign', got 'Likely_pathogenic'
- **`ci_clinvar_047_BRCA1_125746`**
  - expected: `'Benign'`
  - actual:   `'Likely_benign'`
  - reason:   expected 'Benign', got 'Likely_benign'
- **`ci_clinvar_048_SLC9A6_139206`**
  - expected: `'Benign'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Benign', got 'Likely_pathogenic'
- **`ci_clinvar_050_PMS2_91284`**
  - expected: `'Benign'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Benign', got 'Uncertain_significance'

### Qwen 2.5 7B (local)

- **`drug_moa_002_cetp_genetics_unclear`**
  - expected: `'unclear'`
  - actual:   `'inhibitor'`
  - reason:   expected 'unclear', got 'inhibitor'
- **`drug_moa_003_cetp_neutral_evidence`**
  - expected: `'unclear'`
  - actual:   `'inhibitor'`
  - reason:   expected 'unclear', got 'inhibitor'
- **`vcf_qc_001_count_pass_variants`**
  - expected: `6`
  - actual:   `9`
  - reason:   expected 6, got 9
- **`variant_calling_001_list_heterozygous_variants`**
  - expected: `['chr1:1000:A:T', 'chr1:2000:G:C', 'chr1:4000:C:G', 'chr2:1500:A:G', 'chr2:2500:G:T', 'chr3:6000:A:G']`
  - actual:   `['chr1:100:A:T', 'chr2:200:C:G']`
  - reason:   missing=['chr1:1000:A:T', 'chr1:2000:G:C', 'chr1:4000:C:G', 'chr2:1500:A:G', 'chr2:2500:G:T', 'chr3:6000:A:G'] extra=['chr1:100:A:T', 'chr2:200:C:G']
- **`variant_filtering_004_missense_combined_annotations`**
  - expected: `['chr1:1000:A:T', 'chr2:1500:A:G', 'chr2:3500:C:G', 'chr3:3000:C:T', 'chr4:2000:C:T', 'chr5:1000:G:C', 'chr6:1000:A:T', 'chr7:2000:T:C']`
  - actual:   `['rs123456', 'rs789012', 'rs345678']`
  - reason:   missing=['chr1:1000:A:T', 'chr2:1500:A:G', 'chr2:3500:C:G', 'chr3:3000:C:T', 'chr4:2000:C:T', 'chr5:1000:G:C', 'chr6:1000:A:T', 'chr7:2000:T:C'] extra=['rs123456', 'rs345678', 'rs789012']
- **`variant_filtering_003_multi_condition`**
  - expected: `2`
  - actual:   `0`
  - reason:   expected 2, got 0
- **`variant_filtering_001_pass_and_dp30`**
  - expected: `5`
  - actual:   `0`
  - reason:   expected 5, got 0
- **`vcf_qc_002_titv_ratio`**
  - expected: `1.5`
  - actual:   `0`
  - reason:   |0.0 - 1.5| = 1.5; abs_tol=0.01, rel_tol=0.005 -> fail
- **`ci_clinvar_003_MLH1_89672`**
  - expected: `'Pathogenic'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Pathogenic', got 'Uncertain_significance'
- **`ci_clinvar_013_RUNX1_561243`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_015_F8_368117`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_016_HNF1A_435424`**
  - expected: `'Likely_pathogenic'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_pathogenic', got 'Pathogenic'
- **`ci_clinvar_022_HNF4A_3358877`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Likely_pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Likely_pathogenic'
- **`ci_clinvar_024_RYR1_1210315`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Pathogenic'
- **`ci_clinvar_026_GAA_499380`**
  - expected: `'Uncertain_significance'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Uncertain_significance', got 'Pathogenic'
- **`ci_clinvar_031_UBE3A_386114`**
  - expected: `'Likely_benign'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Likely_benign', got 'Uncertain_significance'
- **`ci_clinvar_034_BRCA2_215603`**
  - expected: `'Likely_benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_benign', got 'Pathogenic'
- **`ci_clinvar_036_BRCA1_427301`**
  - expected: `'Likely_benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_benign', got 'Pathogenic'
- **`ci_clinvar_037_MSH2_91006`**
  - expected: `'Likely_benign'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Likely_benign', got 'Uncertain_significance'
- **`ci_clinvar_038_BRCA2_427540`**
  - expected: `'Likely_benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_benign', got 'Pathogenic'
- **`ci_clinvar_039_RUNX1_3791501`**
  - expected: `'Likely_benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Likely_benign', got 'Pathogenic'
- **`ci_clinvar_041_BRCA2_209738`**
  - expected: `'Benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Benign', got 'Pathogenic'
- **`ci_clinvar_043_MYH7_164334`**
  - expected: `'Benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Benign', got 'Pathogenic'
- **`ci_clinvar_047_BRCA1_125746`**
  - expected: `'Benign'`
  - actual:   `'Uncertain_significance'`
  - reason:   expected 'Benign', got 'Uncertain_significance'
- **`ci_clinvar_048_SLC9A6_139206`**
  - expected: `'Benign'`
  - actual:   `'Pathogenic'`
  - reason:   expected 'Benign', got 'Pathogenic'
