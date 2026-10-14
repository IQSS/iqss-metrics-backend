# iqss-metrics-backend

# Description of the Backend setup

The Metrics dashboard contains three different parts:

1. The backend. This part aggregates the data.
2. The frontend. This part uses the aggregated data and displays the chart.
3. The IQSS website. The front end is embedded in an iframe on iq.harvard.edu/metrics

# Backend architecture

In most cases the scripts has two steps:

1. Harvesting the data. Which means accessing the data source and saving the result. 
2. Aggregating the data. Which means preparing the data in the desired format for the front end. Data is filtered, summarized, grouped, counted etc. 

Scripts are written in Python and uses Pandas as the library for data manipulation. There are some custom functions in myfunctions.py. All data is written as a TSV in the front end repository. 

## Sources

The following sources are used:

- Google sheets. 
- Aggregated Dataverse data
- Dataverse API
- Github
- RT ticketing system



## Business Operations

Uses a Google spreadsheet. 

Updates: The department edits the number on a monthly basis. 

Contact: Pat. 

## Center for Geographical Analysis (CGA)

Uses a serie of google Forms. The data from the spreadsheets is aggregated. 

Contact: Wendy

Update: continuous

## Client Support Services (CSS)

For now, it uses google spreadsheet. In the future the RT-connection will be used. 

Updates: Every FY

Contacts: Soner and Randy

## Dataverse

Uses a couple of sources. The most important source is the aggregated data from all dataverses installation. This aggregation is done on https://dataversemetrics.odum.unc.edu/dataverse-metrics/ and copied.

Dataverse TV. Spreadsheet with videos about dataverse. 

Github: Number of installation and also some infor about contributors

RT-API to harvest the number of requests for dataverse. 

Contact: Sonia for the Support part and Danny for the rest.

## Dataverse PM daily metrics

`dataverse_pm.py` implements [Dataverse PM #596](https://github.com/IQSS/dataverse-pm/issues/596)
using the project issue/PR query spreadsheet and the
[Dataverse recipes](https://github.com/gdcc/dataverse-recipes/tree/main/python/metrics).
The existing daily workflow calls `harvest_dataverse_pm(output_dir)` and publishes
`assets/data/dataverse-pm-metrics.tsv` in `IQSS/iqss-metrics-dashboard`.

There is one row per UTC collection `date`. Same-day reruns replace that row;
earlier rows are retained. History starts with the first successful run, with no
backfill of missed days or historical spreadsheet values.

| Columns | Meaning |
| --- | --- |
| `date` | UTC collection date. Activity columns below cover the **previous** UTC calendar day, midnight inclusive to the next midnight exclusive. |
| `hub_record_date` | Actual timestamp of the selected Harvard Hub observation (UTC). It can precede the collection date. |
| `github_open_issues` | Current open issues in `IQSS/dataverse`, including backlog. |
| `github_open_prs` | Current open, non-draft PRs in `IQSS/dataverse`. |
| `github_new_issues`, `github_new_prs` | Issues/PRs created during the activity day. New PRs include drafts. |
| `github_closed_issues`, `github_merged_prs` | Issues closed and PRs merged during the activity day. |
| `github_closed_bugs` | Issues closed during the activity day carrying the exact `Type: Bug` label. A blocker label alone does not qualify. |
| `dataverse_releases`, `dataverse_frontend_releases` | Non-draft, non-prerelease releases published during the activity day in `IQSS/dataverse` and `IQSS/dataverse-frontend`, respectively. |
| `installations_total` | Number of entries in the [installation registry](https://iqss.github.io/dataverse-installations/data/data.json) at collection time. |
| `installations_responding` | Distinct Hub installations with an observation during the current UTC month, through the collection date. This is a month-to-date snapshot. |
| `harvard_collections`, `harvard_datasets`, `harvard_files`, `harvard_downloads` | Latest Harvard Hub totals: collections, **local** datasets, files, and cumulative downloads. Harvested datasets are excluded. |
| `rt_new`, `rt_closed` | Unique tickets created/resolved during the activity day in the whole `dataverse_support` queue. Closed tickets must currently have `resolved` status. |

GitHub searches use `repo:IQSS/dataverse`, the appropriate `is:issue`/`is:pr`
qualifier, and `created:`, `closed:`, or `merged:` with the activity date. Open
totals use `is:open`, with `draft:false` only for open PRs. These are actual open
snapshots, replacing the spreadsheet's creation/update-date approximations.
Search counts and labels reflect GitHub's state when collected; this is not an
event-history reconstruction of reopened tickets or later label changes.

The collector resolves Harvard's current Hub ID using hostname
`dataverse.harvard.edu`, queries current and previous month observations, and
chooses the newest Harvard record. It preserves that record's timestamp rather
than presenting older Hub data as a fresh measurement. Sum daily activity counts
for period reports; use the applicable snapshot for open/installation totals and
Harvard cumulative totals, **not their sum**. Missing collection days remain gaps.
Storage totals, percentage changes, and trend calculations are deferred.

The collector uses the existing `RT_USER` and `RT_PASSWORD` credentials.
`GITHUB_TOKEN` is supplied by GitHub Actions; authenticated local runs can also
set it to avoid the lower anonymous API limits. HTTP errors, incomplete GitHub
searches, missing Harvard observations, invalid counts, and incompatible TSV
headers fail the run. The TSV is replaced atomically only after the complete row
has been collected; errors preserve the previous file.

Run the tests with `pipenv run python -m unittest discover -v`. To run only this
collector locally after setting the environment variables and preparing `out`:

```sh
pipenv run python -c 'from dataverse_pm import harvest_dataverse_pm; harvest_dataverse_pm("./out")'
```

### Temporary CGA training omission

The scheduled run on October 14, 2026 failed because the training export returned
a Google "Page Not Found" HTML page instead of TSV, causing the lookup of
`Date of the training workshop` to fail. The `cga_training_aggr()` call is
temporarily commented out and harvesting that feed is skipped so its HTML error
page cannot replace the last valid raw TSV. Its implementation and the last
published training files are preserved. Restore harvesting and aggregation after
repairing the source URL/access and verifying the column mapping.

## Data Science Services (DSS)

Data is mainly stored in RT, but since DSS want to preparation before it is published, with receive the prepared CSVs. Contact: Steve Worthington

Updates: Yearly

## Program on Survey Research (PSR)

Uses a google sheet with the aggregated data. 

Updates: Yearly

Contact: Chase



## Research computing (RC)

Uses a Google sheet for now, with aggregated data. After the migration of RCE we will look at the at this again.

Contact: Len



# Installing and Running

## Requirements 

pyenv ```brew install pyenv```

pipenv ```brew install pipenv```


## .env file
an .env file in this directory with credentials and secret/links (or
ENV variables set on command line)

Example.

```
$ cat .env
SHEET_URL_BUSINESS_OPERATIONS="XXSECRET"
SHEET_URL_CSS="XXSECRET"
SHEET_URL_PSR="XXSECRET"
SHEET_URL_MAIN_AND_RESEARCH_COMPUTING="XXSECRET"
SHEET_URL_DATAVERSE="XXSECRET"
SHEET_URL_CGA_LICENSE_REQUEST="XXSECRET"
SHEET_URL_CGA_TRAINING_REGISTRATION="XXSECRET"
SHEET_URL_CGA_EVENT_REGISTRATION="XXSECRET"
SHEET_URL_CGA_GIS_APPLICATION="XXSECRET"
SHEET_URL_CGA_CONTACT="XXSECRET"
SHEET_URL_CGA_WORKSHOP_EVALUATIONS="XXSECRET"
RT_USER="XXSECRET"
RT_PASSWORD="XXSECRET"
```

## Running
make build run 

`build`: Installs pre-requisite libraries and git pull iqss-metrics-dashboard and 

`run`: Runs the processing. Files updated in ./out which is symlink into iqss-metrics-dashboard repo

At this point look around at out or do a git diff in ./iqss-metrics-dashboard to see if it's good... 
This part will be automatic after Erik confirms.

`clean`: Removes all above.

## How to add a spreadsheet
Use the following method

```
harvest_sheet_tsv_http(output_path, sheet_name, os.getenv("SHEET_URL_ENV"), "A:E", [0..n], gid=0)
```

All URLs are presumed secrets and should live in the `.env` file above. The sheet url also defines which sheet tab 
to pull from

### Example

I needed to add the spreadsheet, selecting A through D, but only returning the columns with index 0, 2, and 3, 
on the second tab sheet entitled "Z"

https://docs.google.com/spreadsheets/d/1F7fcSJoPzUloWMkigLlzJW6r9zGuurtKiAcQirFS8kU

If I click on "Z" tab, the window location becomes

https://docs.google.com/spreadsheets/d/1F7fcSJoPzUloWMkigLlzJW6r9zGuurtKiAcQirFS8kU/edit#gid=831621854

The `gid` is the id of the tab.

Therefore, to harvest this sheet, you would first add the URL to .env, and in your harvester, run  the following:

```
harvest_sheet_tsv_http(output_path, "test_sheet", os.getenv("SHEET_URL_ENV"), "A:D", [0,2,3], gid=831621854)
```

Note that by default gid=0 meaning first tab on the sheet. gid is optional when a sheet has 1 tab.

## Secrets
To schedule the above job, you will also need to set the same environment variable in GitHub actions.
Following the above example

`SHEET_URL_ENV="https://docs.google.com/spreadsheets/d/1F7fcSJoPzUloWMkigLlzJW6r9zGuurtKiAcQirFS8kU"`

Set this variable from the GitHub actions secret page. 
See [setting encrypted secrets](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets)

The `IQSS_DASHBOARD_SSH_DEPLOY_KEY` secret is an SSH key used to commit/push to the dashboard. 
It is a [deploy key](https://docs.github.com/en/free-pro-team@latest/developers/overview/managing-deploy-keys) 
configured in the dashboard repo. You don't need this for local development as it is assumed you have 
your own GH key capale of committing/pushing to both repos  

##  Scheduling
The cron specification lives in `.github/workflows/build.yml`

See https://jasonet.co/posts/scheduled-actions/ for more info.

## Workflow
Follow your original workflow. 
* Create a `.py` file for each harvester.
* Add sheet URLs to .env
* Use the `harvest_sheet_tsv_http` function in your harvester to download andd optionally truncate the data from google sheets.
* You can now test. Use `make run`.
* You can (manually) deploy to the production dash by running `make deploy`. 
* Add the same env files to GH actions encrypted secrets store.
* Push to GH.

## Ref
[GitHub actions tutorial](https://lab.github.com/githubtraining/github-actions:-hello-world)
