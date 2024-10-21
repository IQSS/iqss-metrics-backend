#!/bin/sh
curl 'https://xdmod.rc.fas.harvard.edu/controllers/user_interface.php' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: en-US' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cookie: PHPSESSID=; xdmod_token=;' \
  -H 'Origin: https://xdmod.rc.fas.harvard.edu' \
  -H 'Referer: https://xdmod.rc.fas.harvard.edu/' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw 'public_user=false&realm=Jobs&group_by=pi&start_date=2024-01-01&end_date=2024-09-30&timeframe_label=User+Defined&aggregation_unit=Auto&width=916&height=484&scale=1&dataset_type=timeseries&thumbnail=y&query_group=tg_usage&display_type=bar&combine_type=side&limit=1&offset=0&log_scale=n&show_guide_lines=y&show_trend_line=n&show_error_bars=n&show_aggregate_labels=n&show_error_labels=n&hide_tooltip=false&format=csv&legend_type=off&font_size=0&show_title=y&pi_filter=5702&inline=n&operation=get_data'
