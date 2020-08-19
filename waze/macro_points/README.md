For social distancing score we wanted to represent congestion in an area by choosing isochron centers carefully. We settled on a background of points along a grid with some points of interest overlayed, referred to as "macro" and "micro" points in our haphazard jargon, respectively.

Brian hacked macro points as a grid first, which I immediately flagged as potentially problemmatic, because as you go to higher latitudes, the longitude lines get a *lot* closer together, and you end up with vastly more points. I considered a Voronoi cell approach:

![](YXuwg.png)

But I ended up deciding this was overkill. Ended up settling on my first, simpler idea of just picking a longitude and stepping a certain distance west iteratively, collecting points as macro points if they fell within the US border. `lunkard.py` implements this approach and dumps the results in `lunkard.json`. It uses `gz_2010_us_040_00_500k.json` for reference polygons of US states.

`gz_2010_us_050_00_500k.json` has polygons of all counties and county equivalents. I use this with `sort_macros.py` to generate `lunkard_by_county.json`, because Brian wanted macro points for each county separately.

`viz_lunkard.py` was to verify my points were covering the US. It generates a plot that's fun to play with:

![](Screen%20Shot%202020-04-23%20at%2012.05.08%20PM.png)
![](Screen%20Shot%202020-04-23%20at%2012.35.01%20PM.png)
![Alaska](Screen%20Shot%202020-04-23%20at%2012.38.05%20PM.png)

It's neat to see the swirling patterns as points become less dense at the top than the bottom. This is especially pronounced in the case of Alaska.

Then I played with I think Josh's `show_on_map.py` to produce:

![](Screen%20Shot%202020-04-23%20at%201.06.08%20PM.png)
![](Screen%20Shot%202020-04-23%20at%201.08.54%20PM.png)

It looks even prettier, but this script really can't handle more than a few thousand points.
