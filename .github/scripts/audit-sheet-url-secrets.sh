#!/usr/bin/env bash
set -euo pipefail
umask 077

if ! command -v op >/dev/null 2>&1; then
  curl -sS https://downloads.1password.com/linux/keys/1password.asc \
    | sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" \
    | sudo tee /etc/apt/sources.list.d/1password.list >/dev/null

  sudo mkdir -p /etc/debsig/policies/AC2D62742012EA22/
  curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol \
    | sudo tee /etc/debsig/policies/AC2D62742012EA22/1password.pol >/dev/null
  sudo mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22
  curl -sS https://downloads.1password.com/linux/keys/1password.asc \
    | sudo gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg

  sudo apt-get update
  sudo apt-get install -y 1password-cli
fi
op --version

mkdir -p audit
url_file="audit/sheet_urls.env"
report_file="audit/sheet_url_audit.md"

url_names=(
  SHEET_URL_BUSINESS_OPERATIONS
  SHEET_URL_CSS
  SHEET_URL_PSR
  SHEET_URL_MAIN_AND_RESEARCH_COMPUTING
  SHEET_URL_DATAVERSE
  SHEET_URL_CGA_LICENSE_REQUEST
  SHEET_URL_CGA_TRAINING_REGISTRATION
  SHEET_URL_CGA_EVENT_REGISTRATION
  SHEET_URL_CGA_GIS_APPLICATION
  SHEET_URL_CGA_CONTACT
  SHEET_URL_CGA_WORKSHOP_EVALUATIONS
)

: > "${url_file}"
for name in "${url_names[@]}"; do
  printf '%s=%s\n' "${name}" "${!name:-}" >> "${url_file}"
done

{
  echo "# IQSS Metrics Backend Sheet URL Audit"
  echo
  echo "- Repository: ${GITHUB_REPOSITORY}"
  echo "- Run: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
  echo "- Commit: ${GITHUB_SHA}"
  echo "- Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
} > "${report_file}"

probe_sheet() {
  local collection="$1"
  local env_name="$2"
  local gid="$3"
  local range_name="$4"
  local selected_columns="$5"
  local sheet_url="${!env_name:-}"
  local body_file
  local status

  {
    echo "## ${collection}"
    echo
    echo "- env: ${env_name}"
    echo "- present: $([[ -n "${sheet_url}" ]] && echo yes || echo no)"
    echo "- gid: ${gid}"
    echo "- range: ${range_name}"
    echo "- selected column indexes: ${selected_columns:-all}"
  } >> "${report_file}"

  if [[ -z "${sheet_url}" ]]; then
    echo "- result: skipped missing secret" >> "${report_file}"
    echo >> "${report_file}"
    return 0
  fi

  body_file="$(mktemp)"
  status="$(
    curl -L -sS --get \
      --data-urlencode "gid=${gid}" \
      --data-urlencode "format=tsv" \
      --data-urlencode "range=${range_name}" \
      --write-out "%{http_code}" \
      --output "${body_file}" \
      "${sheet_url%/}/export" || true
  )"

  python3 - "${body_file}" "${selected_columns}" "${status}" >> "${report_file}" <<'PY'
import csv
import sys

body_file, selected_columns, status = sys.argv[1:4]
with open(body_file, newline="") as handle:
    rows = list(csv.reader(handle, delimiter="\t"))

headers = rows[0] if rows else []
indexes = []
if selected_columns:
    indexes = [int(value) for value in selected_columns.split(",") if value]

selected = []
for index in indexes:
    if index < len(headers):
        selected.append(headers[index])
    else:
        selected.append(f"<missing index {index}>")

headers_text = " | ".join(headers)
selected_text = " | ".join(selected) if indexes else "all"
if len(headers_text) > 500:
    headers_text = headers_text[:497] + "..."
if len(selected_text) > 500:
    selected_text = selected_text[:497] + "..."

print(f"- http status: {status}")
print(f"- row count: {len(rows)}")
print(f"- column count: {len(headers)}")
print(f"- headers: {headers_text}")
print(f"- selected columns: {selected_text}")
print()
PY
  rm -f "${body_file}"
}

probe_sheet "business_operations" "SHEET_URL_BUSINESS_OPERATIONS" "0" "A:I" ""
probe_sheet "dataverse_tv" "SHEET_URL_DATAVERSE" "0" "A:E" "1,2,3,4,5"
probe_sheet "main_metrics" "SHEET_URL_MAIN_AND_RESEARCH_COMPUTING" "0" "A:H" ""
probe_sheet "psrAdvisesBySchool" "SHEET_URL_PSR" "0" "A:D" ""
probe_sheet "psrAdvisesByRole" "SHEET_URL_PSR" "1079810459" "A:E" ""
probe_sheet "cgaContact" "SHEET_URL_CGA_CONTACT" "279615175" "A:H" "0,5,6,7"
probe_sheet "cgaWorkshopEvaluation" "SHEET_URL_CGA_WORKSHOP_EVALUATIONS" "1803423154" "A:P" "0,1,2,6,7,8,9,10,11,12,13,14,15"
probe_sheet "cgaGISApplication" "SHEET_URL_CGA_GIS_APPLICATION" "1021617292" "A:N" "0,1,5,6,7"
probe_sheet "cgaEventRegistration" "SHEET_URL_CGA_EVENT_REGISTRATION" "340045856" "A:L" "0,1,5,6,7"
probe_sheet "cgaTrainingRegistration" "SHEET_URL_CGA_TRAINING_REGISTRATION" "2068274999" "A:M" "0,1,2,6,7,8,11,12"
probe_sheet "cgaLicenseRequest" "SHEET_URL_CGA_LICENSE_REQUEST" "842362239" "A:L" "0,5,6,7,10,11"
probe_sheet "cssQuarterlyTickets" "SHEET_URL_CSS" "1872220957" "A:F" ""
probe_sheet "cssMonthlyTickets" "SHEET_URL_CSS" "258445490" "A:F" ""
probe_sheet "cssDeviceType" "SHEET_URL_CSS" "1021732063" "A:K" ""
probe_sheet "cssPatronCommunity" "SHEET_URL_CSS" "345883130" "A:W" ""
probe_sheet "cssTypeOfRequestPCMac" "SHEET_URL_CSS" "1854286511" "A:V" ""
probe_sheet "lab_report_master_data" "SHEET_URL_CSS" "799546563" "A:Y" ""

op whoami --account harvarduniversity >/dev/null
op item create \
  --format json \
  --account harvarduniversity \
  --category "Secure Note" \
  --vault "IQSS DevOps" \
  --title "IQSS Metrics Backend Google Sheet URLs - 2026-06-01" \
  notesPlain="$(cat "${report_file}")" \
  "sheet_urls.env[file]=${url_file}" \
  "sheet_url_audit.md[file]=${report_file}" > audit/op_item.json

item_id="$(python3 -c 'import json; print(json.load(open("audit/op_item.json"))["id"])')"
echo "Created 1Password item in IQSS DevOps vault: ${item_id}"
echo
cat "${report_file}"
