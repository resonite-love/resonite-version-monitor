#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

# Historical data
historical_data = """4 June 2025 – 18:17:18 UTC    8 days ago    8412389452125882142    
3 June 2025 – 12:14:21 UTC    9 days ago    7939760756338420742    
3 June 2025 – 11:51:11 UTC    9 days ago    7948424894764595411    
2 June 2025 – 16:57:27 UTC    10 days ago    1324356736896540422    
30 May 2025 – 22:50:42 UTC    13 days ago    448986111114967166    
30 May 2025 – 21:27:04 UTC    13 days ago    4643386648831883116    
30 May 2025 – 00:13:59 UTC    14 days ago    5818570134642961056    
29 May 2025 – 23:02:04 UTC    14 days ago    4281492182895112523 prerelease    
29 May 2025 – 22:03:23 UTC    14 days ago    7489463287389669183 prerelease    
28 May 2025 – 21:31:58 UTC    15 days ago    6378378175103934740    
28 May 2025 – 20:25:26 UTC    15 days ago    4952836035341678743 prerelease    
28 May 2025 – 00:01:47 UTC    16 days ago    6062291764856616116 prerelease    
23 May 2025 – 18:23:53 UTC    20 days ago    2496500126663483193    
23 May 2025 – 00:46:36 UTC    21 days ago    374358282819415153    
23 May 2025 – 00:03:16 UTC    21 days ago    4293697008335354679    
22 May 2025 – 18:46:33 UTC    21 days ago    3079633946942081368 prerelease    
22 May 2025 – 18:16:29 UTC    21 days ago    4913435084070482714 prerelease    
21 May 2025 – 21:15:21 UTC    22 days ago    661992956566181804 prerelease    
21 May 2025 – 20:19:40 UTC    22 days ago    7245794026657946684 prerelease    
21 May 2025 – 19:42:30 UTC    22 days ago    8192040172027211697 prerelease    
21 May 2025 – 18:22:45 UTC    22 days ago    6056806225297646751 prerelease    
21 May 2025 – 04:29:31 UTC    22 days ago    306350934531021390 prerelease    
21 May 2025 – 00:14:16 UTC    23 days ago    5763076026377832691 prerelease    
20 May 2025 – 23:28:51 UTC    23 days ago    3523405963727830634 prerelease    
20 May 2025 – 22:58:57 UTC    23 days ago    3329251671985588337 prerelease    
20 May 2025 – 22:45:09 UTC    23 days ago    8217649568332175058 prerelease    
20 May 2025 – 21:54:04 UTC    23 days ago    4141647269838923698 prerelease    
20 May 2025 – 19:36:15 UTC    23 days ago    7958359567309327526 prerelease    
20 May 2025 – 00:11:52 UTC    24 days ago    7593702414193617327 prerelease    
16 May 2025 – 21:27:03 UTC    27 days ago    4485813256947097851    
16 May 2025 – 00:35:31 UTC    28 days ago    4843605160801601345    
14 May 2025 – 22:38:45 UTC    29 days ago    7456489022502497505    
13 May 2025 – 23:38:58 UTC    30 days ago    8772094806876476032    
13 May 2025 – 17:33:29 UTC    30 days ago    8249381990600809586 prerelease    
9 May 2025 – 19:08:15 UTC    last month    1439904322770232510    
9 May 2025 – 00:30:25 UTC    last month    7519644939576959332    
8 May 2025 – 22:08:56 UTC    last month    5481455891084506063 prerelease    
8 May 2025 – 21:45:51 UTC    last month    4866853367605751153 prerelease    
8 May 2025 – 20:00:52 UTC    last month    5445731077419069907 prerelease    
8 May 2025 – 19:05:20 UTC    last month    7079431632766979851 prerelease    
7 May 2025 – 03:55:22 UTC    last month    5984795350239797963 prerelease    
7 May 2025 – 00:48:47 UTC    last month    1168914493439060083 prerelease    
6 May 2025 – 22:33:03 UTC    last month    2732600837577350034 prerelease    
6 May 2025 – 19:41:25 UTC    last month    7427423357990270495 prerelease    
6 May 2025 – 05:59:47 UTC    last month    5587019514960949241 prerelease    
6 May 2025 – 04:19:42 UTC    last month    2676113727167518322 prerelease    
5 May 2025 – 23:22:11 UTC    last month    1202878549145297163 prerelease    
2 May 2025 – 17:41:12 UTC    last month    4144313492880925392 prerelease    
2 May 2025 – 05:31:10 UTC    last month    800334666958062736 prerelease    
1 May 2025 – 21:32:35 UTC    last month    9188029936522253920    
1 May 2025 – 01:47:13 UTC    last month    187337175316911138 prerelease    
30 April 2025 – 03:05:31 UTC    2 months ago    7385769913194979225 prerelease    
30 April 2025 – 00:14:05 UTC    2 months ago    7119990186857075952 prerelease    
29 April 2025 – 21:48:20 UTC    2 months ago    4289748030414837727 prerelease    
29 April 2025 – 02:51:57 UTC    2 months ago    8176258863373312044 prerelease    
28 April 2025 – 23:35:51 UTC    2 months ago    5771652629050587960 prerelease    
10 April 2025 – 21:52:39 UTC    2 months ago    4946471762566798007    
10 April 2025 – 20:55:07 UTC    2 months ago    2895486396451909388 prerelease    
10 April 2025 – 09:12:02 UTC    2 months ago    7804017418834779674 prerelease    
10 April 2025 – 00:58:24 UTC    2 months ago    7540168789204955111 prerelease    
9 April 2025 – 19:12:01 UTC    2 months ago    8455739234012030760 prerelease    
8 April 2025 – 23:46:14 UTC    2 months ago    4998492167361708474 prerelease    
8 April 2025 – 23:20:16 UTC    2 months ago    3027049114743588122 prerelease    
8 April 2025 – 21:35:24 UTC    2 months ago    4346839274144743506 prerelease    
8 April 2025 – 02:06:01 UTC    2 months ago    4059990648587823161 prerelease    
8 April 2025 – 01:23:15 UTC    2 months ago    9223027635926498129 prerelease    
7 April 2025 – 23:06:55 UTC    2 months ago    8900092249999466161 prerelease    
3 April 2025 – 22:33:07 UTC    2 months ago    8645234934112025399    
1 April 2025 – 08:41:47 UTC    2 months ago    349611396004574698    
1 April 2025 – 07:28:46 UTC    2 months ago    1300551774472972495    
28 March 2025 – 19:37:37 UTC    3 months ago    5158236652015255050    
27 March 2025 – 19:43:01 UTC    3 months ago    8900056277104228303    
25 March 2025 – 22:34:34 UTC    3 months ago    4671307095594816658    
18 March 2025 – 00:30:26 UTC    3 months ago    318539667587941268    
17 March 2025 – 23:01:40 UTC    3 months ago    8097899113441105476    
11 March 2025 – 22:35:32 UTC    3 months ago    829069518740903804    
4 March 2025 – 23:48:55 UTC    3 months ago    7244678051437818916    
26 February 2025 – 03:00:05 UTC    4 months ago    189529380417922997    
25 February 2025 – 22:03:25 UTC    4 months ago    6859103155009274161    
21 February 2025 – 01:45:04 UTC    4 months ago    2589867183535532625    
21 February 2025 – 00:29:27 UTC    4 months ago    3096593909572461992    
19 February 2025 – 00:33:18 UTC    4 months ago    1640514326572325809    
18 February 2025 – 23:18:30 UTC    4 months ago    3286825175622790180 release    
18 February 2025 – 00:09:32 UTC    4 months ago    7142202929531713575    
17 February 2025 – 23:39:06 UTC    4 months ago    6301102380501471896    
17 February 2025 – 21:47:26 UTC    4 months ago    2764801017406518174    
14 February 2025 – 07:23:30 UTC    4 months ago    3030461755301052085 prerelease    
14 February 2025 – 07:04:42 UTC    4 months ago    7380523498946055757    
13 February 2025 – 23:46:02 UTC    4 months ago    148244342832243679 prerelease    
13 February 2025 – 23:30:45 UTC    4 months ago    7072755122696490068    
12 February 2025 – 21:35:06 UTC    4 months ago    8962826505745045848 prerelease    
12 February 2025 – 21:13:50 UTC    4 months ago    8683259493033923167    
11 February 2025 – 00:22:17 UTC    4 months ago    412818807815203824    
10 February 2025 – 22:25:22 UTC    4 months ago    1865903663650940960 prerelease    
7 February 2025 – 21:11:53 UTC    4 months ago    2144288504617765717 prerelease    
5 February 2025 – 21:56:57 UTC    4 months ago    8729567831685354700    
4 February 2025 – 22:45:05 UTC    4 months ago    926412989150436275    
30 January 2025 – 23:33:00 UTC    5 months ago    6225678409896289783    
28 January 2025 – 20:26:38 UTC    5 months ago    4414766211919498514    
25 January 2025 – 20:48:37 UTC    5 months ago    8326587028153178624    
16 January 2025 – 05:46:37 UTC    5 months ago    5704106848238749604 prerelease    
14 January 2025 – 00:32:25 UTC    5 months ago    7311649915017010340    
10 January 2025 – 23:11:39 UTC    5 months ago    485330054964984642    
10 January 2025 – 03:41:51 UTC    5 months ago    6107124791474159802 prerelease    
9 January 2025 – 23:43:30 UTC    5 months ago    7231309808377354879    
7 January 2025 – 23:15:45 UTC    5 months ago    5467136440859128176    
5 January 2025 – 22:07:20 UTC    5 months ago    133525415927931324 prerelease    
4 January 2025 – 22:57:05 UTC    5 months ago    5091573150703026874 prerelease    
26 December 2024 – 23:09:15 UTC    6 months ago    7317037505035009887    
18 December 2024 – 08:03:35 UTC    6 months ago    7784620721219697938    
17 December 2024 – 09:04:42 UTC    6 months ago    447371753641733678    
16 December 2024 – 23:16:36 UTC    6 months ago    536889705477488053    
16 December 2024 – 21:52:52 UTC    6 months ago    3272575603435964304    
13 December 2024 – 22:31:56 UTC    6 months ago    3131132926421788407 prerelease    
12 December 2024 – 21:14:11 UTC    6 months ago    8191166813912607587 prerelease    
12 December 2024 – 09:15:22 UTC    6 months ago    3525623414850525889 prerelease    
11 December 2024 – 23:18:37 UTC    6 months ago    4188066206498953539 prerelease    
11 December 2024 – 08:49:32 UTC    6 months ago    1962254964456478237 prerelease    
10 December 2024 – 23:56:26 UTC    6 months ago    7471651835555989009 prerelease    
10 December 2024 – 09:04:11 UTC    6 months ago    5341928486782498706 prerelease    
10 December 2024 – 08:09:10 UTC    6 months ago    6109509450897693466    
9 December 2024 – 19:29:05 UTC    6 months ago    135499739487298963    
5 December 2024 – 20:04:51 UTC    6 months ago    1704794229673401153 prerelease    
5 December 2024 – 09:15:43 UTC    6 months ago    2382076818505402081 prerelease    
4 December 2024 – 19:51:41 UTC    6 months ago    472299323508335833 prerelease    
2 December 2024 – 20:03:43 UTC    6 months ago    4591919368891207150    
19 November 2024 – 08:37:40 UTC    7 months ago    3371302329714264951 prerelease    
19 November 2024 – 08:05:13 UTC    7 months ago    2836391326131014463    
14 November 2024 – 20:00:07 UTC    7 months ago    8777561274830262077    
13 November 2024 – 07:43:32 UTC    7 months ago    7563477085197004663 prerelease    
12 November 2024 – 22:26:40 UTC    7 months ago    6270485971974165693    
29 October 2024 – 20:38:50 UTC    8 months ago    3269907593548201806    
23 October 2024 – 00:33:58 UTC    8 months ago    5081960274621398689    
22 October 2024 – 19:01:22 UTC    8 months ago    52336512033074753 prerelease    
22 October 2024 – 04:25:38 UTC    8 months ago    848482880684128337 prerelease    
22 October 2024 – 03:52:51 UTC    8 months ago    4339091563695110536 prerelease    
22 October 2024 – 03:44:08 UTC    8 months ago    5549291936332297974 prerelease    
21 October 2024 – 21:52:49 UTC    8 months ago    8474099380526411866 prerelease    
11 October 2024 – 01:00:41 UTC    8 months ago    3028822006182256883 prerelease    
8 October 2024 – 22:37:15 UTC    8 months ago    8252654501983979266    
4 October 2024 – 15:32:39 UTC    8 months ago    46528300973251031"""

def parse_line(line):
    """Parse a single line of historical data."""
    # Remove multiple spaces and normalize
    line = re.sub(r'\s+', ' ', line.strip())
    
    # Pattern to match the date, time, and manifest ID
    # Format: "DD Month YYYY – HH:MM:SS UTC ... ago MANIFEST_ID [branch]"
    pattern = r'(\d+)\s+(\w+)\s+(\d{4})\s+–\s+(\d{2}):(\d{2}):(\d{2})\s+UTC\s+.*?\s+(\d+)\s*(prerelease|release)?'
    
    match = re.match(pattern, line)
    if not match:
        print(f"Failed to parse: {line}")
        return None
    
    day, month, year, hour, minute, second, manifest_id, branch = match.groups()
    
    # Convert month name to number
    months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    
    month_num = months.get(month)
    if not month_num:
        print(f"Unknown month: {month}")
        return None
    
    # Create datetime object
    dt = datetime(int(year), month_num, int(day), int(hour), int(minute), int(second))
    timestamp = dt.isoformat() + 'Z'
    
    # Determine branch (default to public/release)
    if branch == 'prerelease':
        branch_name = 'prerelease'
    else:
        # Both 'release' and no label are considered public/release
        branch_name = 'public'
    
    return {
        'branch': branch_name,
        'entry': {
            'manifestId': manifest_id,
            'timestamp': timestamp,
            'gameVersion': None
        }
    }

def main():
    # Parse all lines
    entries_by_branch = {
        'public': [],
        'prerelease': [],
        'release': []
    }
    
    for line in historical_data.strip().split('\n'):
        if not line.strip():
            continue
            
        parsed = parse_line(line)
        if parsed:
            branch = parsed['branch']
            entry = parsed['entry']
            
            # Add to appropriate branch
            entries_by_branch[branch].append(entry)
            
            # Also add to 'release' branch if it's public
            if branch == 'public':
                entries_by_branch['release'].append(entry.copy())
    
    # Sort entries by timestamp (oldest first)
    for branch in entries_by_branch:
        entries_by_branch[branch].sort(key=lambda x: x['timestamp'])
    
    # Save to versions.json
    output_path = Path(__file__).parent.parent / 'data' / 'versions.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(entries_by_branch, f, indent=2)
    
    print(f"Created versions.json with:")
    for branch, entries in entries_by_branch.items():
        print(f"  {branch}: {len(entries)} entries")
    
    print(f"\nSaved to: {output_path}")

if __name__ == '__main__':
    main()