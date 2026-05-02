# apps-sdk-submission-lint Launch Copy

## Short Description

Offline lint checks for Apps SDK-style submission metadata before review.

## Announcement

`apps-sdk-submission-lint` is a small CLI that scans local JSON app metadata for common submission-readiness gaps: missing names and descriptions, absent privacy policy links, broad CSP domains, incomplete tool annotation hints, missing screenshots, and wording that implies approval or certification.

It is designed for maintainers who want a fast pre-review check in local development or CI. It does not call external services and does not validate against an official submission schema.

Repository: https://github.com/metaimagine/apps-sdk-submission-lint

## Disclaimer

This is an independent lint helper. It is not OpenAI approval, certification, endorsement, or a guarantee that an app will pass any submission review.
