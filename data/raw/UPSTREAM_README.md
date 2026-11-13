# AI certifications dataset

A free JSON dataset of AI certifications from AI Course Check. Each record has the price as the issuer shows it, exam format, validity and who can take it, with the date it was checked. It covers vendor and professional credentials, including agentic AI ones. Stated facts only, each from the issuer's own page.

**This repository is a copy; the site is updated first.** The canonical source is <https://aicoursecheck.com/data/>. A workflow here fetches the files from the site once a week and commits only when they changed.

## Files

| File | What it holds |
|---|---|
| [`credentials.json`](credentials.json) | One record per certification shown on the site. |
| [`changes.json`](changes.json) | Changes the issuers made (prices, retirements, replacements), newest first. |

Each file also carries `schema_version`, `generated_at` (the date of its most recent check) and `count`. `credentials.json` repeats the field list below in its `fields` block.

## How do nulls work?

A fact the issuer doesn't state is `null`, meaning "not stated by the issuer". It does not mean free, unlimited or not applicable. Nothing is estimated or worked out, and there are no ratings, rankings or editorial notes. Prices are never converted.

## How is it checked?

Every record is checked against the issuer's own pages, listed in `source_urls`. `last_checked` is the day of the last check, and `last_changed` the day a check last found a new value. See [how the facts are checked](https://aicoursecheck.com/methodology/), the [changes page](https://aicoursecheck.com/changes/) and [corrections](https://aicoursecheck.com/corrections/).

## Fields

Fields in each record of `credentials.json`, in order.

| Field | Type | Meaning |
|---|---|---|
| `id` | `string` | Our stable id for the credential (also its page slug). |
| `name` | `string` | The credential's name as the issuer writes it. |
| `issuer` | `string` | Issuer id. |
| `issuer_name` | `string` | The issuer's name. |
| `family` | `string \| null` | The issuer's named programme it belongs to, as an id. |
| `kind` | `string` | exam, course-certificate, assessment or microcredential. |
| `level` | `string \| null` | The issuer's own tier word: foundational, associate, professional, specialty or expert. |
| `exam_code` | `string \| null` | Exam code as the issuer writes it (AI-102, AIF-C01). |
| `credential_code` | `string \| null` | The credential's own code or abbreviation (AIGP, AAISM). |
| `eligibility` | `string \| null` | Who can take it, in the issuer's words. |
| `prerequisites` | `string \| null` | Required or recommended experience, in the issuer's words. |
| `price` | `array \| null` | Price rows as the issuer shows them, never converted: label, amount, currency, tax, billing, region_note. |
| `delivery_modes` | `array \| null` | How it can be taken: online-proctored, test-center, self-paced or online-assessment. |
| `proctoring` | `string \| null` | Proctoring as the issuer states it. |
| `exam_length_minutes` | `integer \| null` | Exam length in minutes. |
| `question_count` | `object \| null` | Number of questions: min and max (equal when the issuer states one number). |
| `passing_score` | `string \| null` | The score needed to pass, in the issuer's wording. |
| `validity_months` | `integer \| null` | How long it stays valid, in months. |
| `no_expiry` | `boolean \| null` | true when the issuer states that the credential has no expiry date. |
| `renewal` | `string \| null` | How to renew, in the issuer's words. |
| `languages` | `array \| null` | Exam languages. |
| `status` | `string` | Status in the issuer's word, for example active, beta or announced. |
| `launch_date` | `string \| null` | Launch date (YYYY-MM or YYYY-MM-DD). |
| `retirement_date` | `string \| null` | Retirement date (YYYY-MM or YYYY-MM-DD). |
| `replaced_by` | `string \| null` | Id of the credential the issuer names as its replacement. |
| `replaces` | `array` | Ids of the credentials it replaces. |
| `official_prep` | `string \| null` | Where the issuer says its official preparation is, in its words. |
| `source_urls` | `array` | The issuer's pages the facts come from. |
| `last_checked` | `string` | The day we last checked the record against the issuer's pages (YYYY-MM-DD). |
| `last_changed` | `string \| null` | The day a check last found a changed value (YYYY-MM-DD). |
| `url` | `string` | Where the credential is shown on this site. |

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the full text is in [`LICENSE`](LICENSE). Attribution line:

> AI Course Check (aicoursecheck.com), with a link to <https://aicoursecheck.com/data/>

The license covers the selection and structure of the dataset; issuer names, exam codes and prices are facts from the issuers' own pages.

