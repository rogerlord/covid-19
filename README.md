# covid-19
[![Build status](https://ci.appveyor.com/api/projects/status/hjap7sk0bm8ds37q?svg=true)](https://ci.appveyor.com/project/RogerLord/covid-19)

This project contains COVID-19 related data analysis.

The repository contains functionality to analyse the total amount of COVID-19 cases in various countries (at present the Netherlands, Germany, Sweden, United Kingdom). Due to reporting delays the number of cases reported in a country at any given date T is usually built up out of cases which have occurred and/or been reported a few days prior to T. If the number of cases are rising, this leads to an underestimation of the actual number of cases on date T, whereas if the number of cases are decreasing, this leads to an overestimation. If more detailed datasets are available, nowcasting techniques can be used to correct for this.

The nowcasting techniques used are described [here](/docs/nowcastingcovid19.pdf).

At the moment the repository is actively maintained for the following countries:

* [The Netherlands](/docs/NL.md)
* [Germany](/docs/DE.md)