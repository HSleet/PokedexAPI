-- SQLite
--SELECT Pokemon.PokemonName, Pokemon.PokemonID, Regions."Region of Origin" as "Region"
--from Pokemon
--join Regions on Pokemon.RegionofOrigin == Regions.RecordID
-- SELECT Pokemon.PokemonID, Pokemon.PokedexNumber, Pokemon.PokemonName, Types.Type as "Pokemon Type 1"
    -- FROM Pokemon
    -- JOIN Types ON Pokemon.PrimaryType == Types.RecordID 
    -- LEFT JOIN Types ON Pokemon.SecondaryType == Types.RecordID 
-- UNION 
-- SELECT Pokemon.PokemonID, Pokemon.PokedexNumber, Pokemon.PokemonName, Types.Type as "Pokemon Type 2"
    -- FROM Pokemon
    -- left JOIN Types ON Pokemon.SecondaryType == Types.RecordID 


-- SELECT PokemonID, PokedexNumber, PokemonName, AlternateFormName, t1.Type as "Pokemon Type 1", t2.Type as "Pokemon Type 2"
-- FROM Pokemon
--     left JOIN Types t1 ON PrimaryType == t1.RecordID 
--     left JOIN Types t2 ON SecondaryType == t2.RecordID 
-- WHERE PrimaryType == 5 and SecondaryType == 10 or PrimaryType == 10 and SecondaryType == 5

-- SELECT * FROM Pokemon

-- SELECT Pokemon.*,
--  t1.Type as primary_type,
--  t2.Type as secondary_type, 
--  a1.Ability as primary_ability, 
--  a1.description as primary_ability_description, 
--  a2.Ability as secondary_ability, 
--  a2.description as secondary_ability_description, 
--  a3.Ability as hidden_ability,
--  a3.description as hidden_ability_description, 
--  "Region of Origin" as region_of_origin,
--  e1."Egg Group" as primary_egg_group,
--  e2."Egg Group" as secondary_egg_group,
--  "Game(s) of Origin" as game_of_origin
-- From Pokemon
--     left JOIN Types t1 ON PrimaryType == t1.RecordID 
--     left JOIN Types t2 ON SecondaryType == t2.RecordID 
--     LEFT JOIN Abilities a1 on PrimaryAbility == a1.RecordID
--     LEFT JOIN Abilities a2 on SecondaryAbility == a2.RecordID
--     LEFT JOIN Abilities a3 on HiddenAbility == a3.RecordID
--     LEFT JOIN Regions on RegionofOrigin == Regions.RecordID
--     LEFT JOIN EggGroups e1 on PrimaryEggGroup == e1.RecordID
--     LEFT JOIN EggGroups e2 on SecondaryEggGroup == e2.RecordID
--     LEFT JOIN Games on GameofOrigin == Games.RecordID
-- WHERE PokemonName LIKE "%Ivy%";


SELECT PokemonID, PokedexNumber, PokemonName, AlternateFormName, t1.RecordID as "primaryTypeId", t1.Type as "Pokemon Type 1",
t2.RecordID as "secondaryTypeId", t2.Type as "Pokemon Type 2", Regions."Region of Origin" as Region, Regions.RecordID as regionID,
Games."Game(s) of Origin" as gameOfOrigin, Games.RecordID as gameID, e1.RecordID as eggGroupID_1, e1."Egg Group" as primaryEggGroup,
e2.RecordID as eggGroupID_2, e2."Egg Group" as secondEggGroup, a1.Ability as primaryAbility, a1.RecordID as AbilityId_1, a1.description as primaryAbilityDescription, 
a2.Ability as secondaryAbility, a2.RecordID as AbilityId_2, a2.description as secondaryAbilityDescription, a3.Ability as hiddenAbility, 
a3.RecordID as AbilityId_3, a3.description as hiddenAbilityDescription        
FROM Pokemon
        left JOIN Types t1 ON PrimaryType == t1.RecordID 
        left JOIN Types t2 ON SecondaryType == t2.RecordID 
        left JOIN Regions  ON RegionofOrigin == Regions.RecordID
        left JOIN Games on GameofOrigin == Games.RecordID
        LEFT JOIN EggGroups e1 on PrimaryEggGroup == e1.RecordID
        LEFT JOIN EggGroups e2 on SecondaryEggGroup == e2.RecordID
--  WHERE ((t1.RecordID == 10 and t2.Type == "Poison") or (t1.Type == "Poison" and t2.RecordID == 10)) AND RegionID == 6
 WHERE (( eggGroupID_1 == 11 and secondary_egg_group == "Grass")  or (primary_egg_group == "Monster" and eggGroupID_2 == 10))

