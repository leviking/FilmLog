CREATE VIEW FilmTestsView AS
SELECT FilmTypes.name AS filmName, FilmTypes.iso AS filmISO, 
developer, SEC_TO_TIME(time) AS devTime, Filters.code AS filter,
lux, fstop,
gamma, contrastIndex
FROM FilmTests
JOIN DevRecipes ON DevRecipes.userID = FilmTests.userID
    AND DevRecipes.devRecipeID = FilmTests.devRecipeID
JOIN FilmTypes ON FilmTypes.userID = FilmTests.userID
    AND FilmTypes.filmTypeID = FilmTests.filmTypeID
JOIN Filters ON Filters.userID = FilmTests.userID
    AND Filters.filterID = FilmTests.filterID
ORDER BY filmName, filmISO, devTime;
