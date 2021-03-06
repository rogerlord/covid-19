# The Netherlands

The datasets on which the below analysis is based are provided [here](https://data.rivm.nl/geonetwork/srv/dut/catalog.search#/metadata/2c4357c8-76e4-4662-9574-1deb8a73f724?tab=relations) on a daily basis by the [RIVM](https://rivm.nl/en), the Dutch National Institute for Public Health and the Environment. The nowcasts could not have been possible without the repository of [Marino van Zelst](https://github.com/mzelst) and [Edwin Veldhuizen](https://github.com/edwinveldhuizen) who keep a historical archive of the RIVM datasets [here](https://github.com/mzelst/covid-19/).

The nowcasting techniques used are described [here](nowcastingcovid19.pdf).

The below graph, which will be updated on a daily basis, shows the currently known amount of reported positive tests for the last 30 days ("*Actual (not fully known)*"), the nowcast for the reported amount of positive tests on a given date ("*Nowcast*"), as well as a 7-day rolling average of the number of reported positive tests (based on the nowcasts, "*Nowcast (7-day rolling average)*"). The nowcasts are generated by using a so-called Poisson chain ladder.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_plot.png" alt="COVID-19 positive tests - actual vs. nowcast - the Netherlands"/>
</p>

The next graph puts shows the 7-day rolling averages of the nowcast ("*Nowcast*") based on all information that is currently available, together with the past performance of the nowcast ("*Nowcast (same-day)*"), the gross reported number of positive tests ("*Gross*") as well as the actual data ("*Actual (not fully known)*").

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_nowcast_performance.png" alt="COVID-19 - 7-day rolling average of positive tests - the Netherlands"/>
</p>

The error of the (7-day rolling average of the) nowcast can be seen in the graph below, where the error of the nowcast for various parameters (β = 0 corresponds to equal weights for all observations, the higher the value of β, the more weight is placed on recent observations) is compared to the error of the gross reported number of positive tests.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_nowcast_error.png" alt="COVID-19 - error in same-day nowcast of 7-day rolling average of positive tests - the Netherlands"/>
</p>

Additionally, the below graph shows the reported number of positive tests in the last 7 days per municipal health region (*GGD regio*). The measure used here is the gross increase in the reported positive tests. The scale stops at 250 positive tests per 100,000 inhabitants in correspondence with the risk levels defined by the [RIVM](https://coronadashboard.government.nl/over-risiconiveaus).

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_daily_cases_per_ggd_region_plot.jpg" alt="COVID-19 positive tests per municipal health region in the Netherlands"/>
</p>

Finally, the plot below has been inspired by [Marc Bevand](https://github.com/mbevand)'s heatmap of COVID-19 cases in Florida, which can be found [here](https://github.com/mbevand/florida-covid19-line-list-data). Each pixel represents a 1-day time period and age group. The intensity of each pixel indicates the
percentage of positive tests in that age group, relative to all cases reported on that day.

<p align="center">
  <img src="https://raw.githubusercontent.com/rogerlord/covid-19/master/plots/nl/COVID-19_heatmap_plot.jpg" alt="Heatmap of COVID-19 positive tests in the Netherlands"/>
</p>