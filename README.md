# README #

Astroobs provides astronomy ephemeris (airmass, azimuth, altitude, etc) of a night sky target as a function of the date-time and the longitude/latitude of the observer.
A list of international observatories is provided as well as a SIMBAD-querier to easily import targets.
This package is based on pyephem ephemeris calculations. The main difference with this latter package is that astroobs provides a very straight-forward library for the observer to get the critical information in order to plan an observation.
e.g. plotting airmass vs date-time of "Betelgeuse" at "VLT" on 2015/12/25 takes a couple of lines only.