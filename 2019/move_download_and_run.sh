rm clues.csv
mv ~/Downloads/Hunt\ Clue\ Tracker\ 2019*.csv clues.csv
python geocode.py clues.csv| tee clues.kml
