ALTER TABLE DevRecipes
    ADD COLUMN prebath ENUM ('No', 'Water') NOT NULL DEFAULT 'No' AFTER temperature;
