# covid-19
[![Build status](https://ci.appveyor.com/api/projects/status/hjap7sk0bm8ds37q?svg=true)](https://ci.appveyor.com/project/RogerLord/covid-19)

This project contains COVID-19 related data analysis.

The currently available set concerns the number of new COVID-19 infections in the Netherlands. The [COVID-19 / Corona dashboard](https://coronadashboard.rijksoverheid.nl/) provided by the Dutch government shows, on a day to day basis, the change in the total amount of reported infections in the Netherlands. The dataset on which this dashboard is based is provided [here](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724?tab=relations) by the RIVM. As the change from T-1 to T is based on infections occurring on T, but also on infections that have occurred at previous dates or corrections that have been made to the dataset, the current dashboard does not give an accurate estimate of the amount of infections occurring on T. The reported number does however appear to be interpreted as such.

The below graph, which will be updated on a daily basis, shows the currently known reported infections for the last 30 days ("*Current data*"), the forecast for the reported infections on a given date ("*Forecast*"), as well as a 7-day rolling average of the number of reported infections (based on the forecasts, "*7-day rolling average*"). As the number of reported infections usually does not seem to change much after 14 days, we only adjust / forecast the last 14 observations. The forecast for T is found by regressing past same day observations on the currently known reported infections for that date, and using the resulting relation on the current observation for T.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_plot.png" alt="COVID-19 daily infections in the Netherlands"/>
</p>

The forecasts have been made possible with the stored RIVM datasets of [Marino van Zelst](https://github.com/mzelst) and [Edwin van Veldhuizen](https://github.com/edwinveldhuizen) which can be found [here](https://github.com/mzelst/covid-19/).

Additionally, the below graph shows a 7-day rolling average of the number of reported infections per municipal health region (*GGD regio*). As it is difficult to
adjust / forecast in regions where little to no infections are occurring, the measure used here is the increase in the reported infections over the last 21 days. We
use a period of 21 days here as the number of reported infections for a given date is usually very stable after 21 days. Changes for older dates (usually downward
corrections) reflect errors in reporting, rather than actual reported infections in the last weeks, which is what we are interested in here. The chosen threshold (50.0 / 7, roughly 7.1) is based on the threshold in Germany, where measures are imposed on a region if the number of reported infections in a 7-day period rises to the level of 50.0 or above.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_per_ggd_region_plot.jpg" alt="COVID-19 daily infections per municipal health region in the Netherlands"/>
</p>

Finally, the plot below has been inspired by [Marc Bevand](https://github.com/mbevand)'s heatmap of COVID-19 cases in Florida, which can be found [here](https://github.com/mbevand/florida-covid19-line-list-data). Each pixel represents a 1-day time period and age group. The intensity of each pixel indicates the
percentage of infections in that age group, relative to all cases reported on that day.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_heatmap_plot.jpg" alt="Heatmap of COVID-19 cases in the Netherlands"/>
</p>