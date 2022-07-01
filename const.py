"""Provides constants for formula_one."""

DOMAIN = "formula_one"

KEY_DRIVERS = "drivers"
KEY_CONSTRUCTORS = "constructors"
KEY_SEASON = "season"

URL_DRIVERS = "http://ergast.com/api/f1/current/driverStandings.json"
URL_CONSTRUCTORS = "http://ergast.com/api/f1/current/constructorStandings.json"
URL_SEASON = "http://ergast.com/api/f1/current.json"

ERR_JSON_DRIVERS = '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"error","DriverStandings":[{"position":"1","positionText":"1","points":"error","wins":"error","Driver":{"driverId":"error","givenName":"error","familyName":"error","nationality":"error"},"Constructors":[{"constructorId":"error","name":"error","nationality":"error"}]}]}]}}'
ERR_JSON_CONSTRUCTORS = '{"StandingsTable":{"season":"error","StandingsLists":[{"season":"error","round":"1","ConstructorStandings":[{"position":"1","positionText":"1","points":"0","wins":"0","Constructor":{"constructorId":"error","url":"error","name":"error","nationality":"error"}}]}]}}'
ERR_JSON_SEASON = '{"xmlns":"http://ergast.com/mrd/1.5","series":"f1","url":"http://ergast.com/api/f1/current.json","limit":"30","offset":"0","total":"1","RaceTable":{"season":"error","Races":[{"season":"error","round":"1","url":"error","raceName":"error","Circuit":{"circuitId":"error","url":"error","circuitName":"error","Location":{"lat":"error","long":"error","locality":"error","country":"error"}},"date":"2022-03-20","time":"15:00:00Z","FirstPractice":{"date":"2022-03-18","time":"12:00:00Z"},"SecondPractice":{"date":"2022-03-18","time":"15:00:00Z"},"ThirdPractice":{"date":"2022-03-19","time":"12:00:00Z"},"Qualifying":{"date":"2022-03-19","time":"15:00:00Z"}}]}}'
