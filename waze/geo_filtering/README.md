Waze had three kinds of messages that we might consider using: alerts, irregularities, and jams. `pretty_X.json` are short examples of each so I'd have a sense of what's there and how to navigate to fields I cared about.

`utah.json` has detailed information about the geographical boundaries of the state and all its counties, among other info. `ohio.json` just has the outline of Ohio. I use these as input in my filtering scripts.

`geo_polygon_and_time_filter.py` was for filtering massive corpuses of Waze information to only retain things that fell inside states we cared about. It's an evolution of something Brian wrote. I had it spit out the resulting records grouped by hour of the week (168 buckets).

`geo_polygon_and_time_filter_daily.py` is an evolution of the not-daily version that spits out the records collected by day. This was because Franz wanted files in this form for his analysis.

Formerly in this directory was `baselines_map.pkl`, a map from (state, county) -> a dataframe of record counts against week-hours. I must have deleted the script I used to generate this, and I later learned that (state, county) isn't enough for uniqueness: My favorite example is how ('Maryland', 'Baltimore') can refer to the county or the independent city with non-overlapping borders. It was also 31.5 MB, so I deleted it, but I mention it because it forms the basis for how we were finding some relative traffic volumes.
