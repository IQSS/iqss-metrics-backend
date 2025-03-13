#!/bin/sh

curl -x socks5h://localhost:1080 'https://xdmod.rc.fas.harvard.edu/controllers/metric_explorer.php' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Cache-Control: max-age=0' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -b 'PHPSESSID=f38qu0smp2gcca2dragccbfkc3; xdmod_token=d05d7278174e97870a0ef80e057431b8' \
  -H 'Origin: https://xdmod.rc.fas.harvard.edu' \
  -H 'Referer: https://xdmod.rc.fas.harvard.edu/index.php' \
  -H 'Sec-Fetch-Dest: document' \
  -H 'Sec-Fetch-Mode: navigate' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-User: ?1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --data-raw 'show_title=y&timeseries=y&aggregation_unit=Auto&start_date=2025-02-01&end_date=2025-02-28&global_filters=%257B%2522data%2522%253A%255B%255D%252C%2522total%2522%253A0%257D&title=untitled+query+15&show_filters=true&show_warnings=true&show_remainder=false&start=0&limit=10&timeframe_label=Previous+month&operation=get_data&data_series=%255B%257B%2522group_by%2522%253A%2522gpucount%2522%252C%2522color%2522%253A%2522auto%2522%252C%2522log_scale%2522%253Afalse%252C%2522std_err%2522%253Afalse%252C%2522value_labels%2522%253Afalse%252C%2522display_type%2522%253A%2522line%2522%252C%2522combine_type%2522%253A%2522side%2522%252C%2522sort_type%2522%253A%2522value_desc%2522%252C%2522ignore_global%2522%253Afalse%252C%2522long_legend%2522%253Atrue%252C%2522x_axis%2522%253Afalse%252C%2522has_std_err%2522%253Afalse%252C%2522trend_line%2522%253Afalse%252C%2522line_type%2522%253A%2522Solid%2522%252C%2522line_width%2522%253A2%252C%2522shadow%2522%253Afalse%252C%2522filters%2522%253A%257B%2522data%2522%253A%255B%255D%252C%2522total%2522%253A0%257D%252C%2522z_index%2522%253A0%252C%2522visibility%2522%253Anull%252C%2522enabled%2522%253Atrue%252C%2522metric%2522%253A%2522utilization%2522%252C%2522realm%2522%253A%2522Jobs%2522%252C%2522category%2522%253A%2522Jobs%2522%252C%2522id%2522%253A-1124996922107757%257D%255D&swap_xy=false&share_y_axis=false&hide_tooltip=false&show_guide_lines=y&showContextMenu=y&scale=1&format=png&width=916&height=484&legend_type=bottom_center&font_size=3&featured=false&trendLineEnabled=undefined&x_axis=%257B%257D&y_axis=%257B%257D&legend=%257B%257D&defaultDatasetConfig=%257B%257D&controller_module=metric_explorer&inline=n' \
  --output p.png