For this subproject I was trying to answer the question "How long do Waze alerts live for?" Seth gave me a firehose to basically query for everything that fell within certain states, which I set to run on a cron job every minute, so I could see when things arrived and when they dropped off. Then in my own script I turned these output files into a bunch of histograms.

![](histogram.png)