ALTER TABLE FilmTypes
  ADD COLUMN displayColor INT UNSIGNED NOT NULL DEFAULT 0 AFTER kind;
