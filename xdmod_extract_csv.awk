#!/usr/bin/awk -f

BEGIN {
    FS = "\n";           # Set the field separator to newline
    RS = "---------\n";  # Set the record separator to '---------\n'
}

{
    # Remove any leading or trailing whitespace
    gsub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", $0)

    # Skip empty records
    if ($0 == "") next

    # Alternate between metadata and data blocks
    if (NR % 2 == 1) {
        # Metadata block
        meta_block = $0

        # Parse metadata
        split(meta_block, meta_lines, "\n")
        title = ""
        pi = ""
        start_date = ""
        end_date = ""
        for (i in meta_lines) {
            line = meta_lines[i]
            line = gensub(/^[ \t\r\n]+|[ \t\r\n]+$/, "", "g", line)  # Trim whitespace
            if (line == "") continue

            if (line == "title") {
                title = gensub(/"/, "", "g", meta_lines[++i])
                title = gensub(":", "", "g", title)
                title = gensub(/[ \t]+/, "_", "g", title)
            } else if (line == "parameters") {
                params = gensub(/"/, "", "g", meta_lines[++i])
                split(params, param_parts, "=")
                if (length(param_parts) >= 2) {
                    pi = gensub(/^[ \t]+|[ \t]+$/, "", "g", param_parts[2])
                }
            } else if (line == "start,end") {
                dates = meta_lines[++i]
                split(dates, date_parts, ",")
                start_date = date_parts[1]
                end_date = date_parts[2]
            }
        }
    } else {
        # Data block
        data_block = $0

        # Parse data
        split(data_block, data_lines, "\n")
        header_line = data_lines[1]
        header_fields = split(header_line, header_parts, ",")
        if (header_fields >= 2) {
            data_header = gensub(/"/, "", "g", header_parts[2])
            # Remove PI in square brackets
            data_header = gensub(/^\[.*\]\s*/, "", "g", data_header)
            data_header = gensub(/[ \t]+/, "_", "g", data_header)
        } else {
            data_header = "Data"
        }

        # Construct filename
        filename = title "_" pi "_" data_header "_" start_date "_" end_date ".csv"
        filename = gensub(/[\/\\:*?"<>|]/, "", "g", filename)  # Remove invalid filename characters

        # Write data to file
        file = filename
        print data_lines[1] > file  # Write header
        for (i = 2; i <= length(data_lines); i++) {
            print data_lines[i] >> file  # Append data
        }
        close(file)
        print "Saved " filename
    }
}
