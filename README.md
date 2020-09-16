# iqss-metrics-backend

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

At this point look around at out or do a git diff in ./iqss-metrics-dashboard to see if its good... This part will be automatic after Erik confirms.

`clean`: Removes all above.

