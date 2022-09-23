import sqlite3 as sql3
import pandas as pd
from flasgger import Swagger
from markupsafe import escape
from flask import Flask, request, abort

app = Flask(__name__)
swagger = Swagger(app)


@app.route("/pokemons", methods=["GET"])
def get_all_pokemons():
    pokemon_filters = request.args
    type_filters = pokemon_filters.getlist("type",)
    region_filter = pokemon_filters.get("region",)
    game_filter = pokemon_filters.get("game",)
    egg_groups = pokemon_filters.getlist("eggGroup")
    ability_filter = pokemon_filters.get("ability")
    if len(pokemon_filters) == 0:   # If no filter arg is given, returns the whole list of pokemons
        pokemon_list = get_pokemon_data()
    else:
        query_conditions = []                   # initialize query conditions list
        if type_filters:
            if len(type_filters)==2:                # if 2 types are selected
                types_condition = []                # initialize the conditional statement for the query
                alternate_types_condition = []      # initialize the alternative conditional statement for the query
                for pokemon_type in type_filters:   # to check alternate type order
                    try:                            # try to convert the args to integer to find pokemons by their type ID
                        types_condition.append(f"t1.RecordID == {int(pokemon_type)}")   # append condition to the list of conditions
                        alternate_types_condition.append(f"t2.RecordID == {int(pokemon_type)}") # and the alternate form
                    except ValueError:
                        pokemon_type = pokemon_type.capitalize()
                        types_condition.append(f"t1.Type == \"{pokemon_type}\"")    # If the args could not be converted to integers
                        alternate_types_condition.append(f"t2.Type == \"{pokemon_type}\"")  # Do the query with the pokemon type string
                final_types_conditions = f"(({types_condition[0]} AND {alternate_types_condition[1]}) OR ({types_condition[1]} AND {alternate_types_condition[0]}))"
                query_conditions.append(f"({final_types_conditions})")      # Appending the resulting condition statement to the list of conditions for the query
            
            elif len(type_filters)==1:         
                pokemon_type = type_filters[0]
                try:
                    # If a single type is given as a filter, try to convert it to int so an ID is used to find
                    # pokemons of that type.
                    query_conditions.append(f"(t1.RecordID == {int(pokemon_type)} OR t2.RecordID == {int(pokemon_type)})")                
                except ValueError:
                    pokemon_type = pokemon_type.capitalize()
                    # If it can't be converted to integer, then try to find it directly with its type.
                    query_conditions.append(f"(t1.Type == \"{pokemon_type}\" OR t2.Type == \"{pokemon_type}\")")
            elif len(type_filters)>2:
                abort(400, "Pokemons can only have 2 types")

        # Do the same with the Egg groups and abilities
        if egg_groups:
            if len(egg_groups)==2:
                eggs_condition = []
                alternate_eggs_condition = []
                for egg_type in egg_groups:
                    try:
                        eggs_condition.append(f"eggGroupID_1 == {int(egg_type)}")
                        alternate_eggs_condition.append(f"eggGroupID_2 == {int(egg_type)}")
                    except ValueError:
                        egg_type = egg_type.capitalize
                        eggs_condition.append(f"primaryEggGroup == \"{egg_type}\"")
                        alternate_eggs_condition.append(f"secondaryEggGroup == \"{egg_type}\"")
                final_eggs_conditions = f"(({eggs_condition[0]} AND {alternate_eggs_condition[1]}) \
                    OR ({eggs_condition[1]} AND {alternate_eggs_condition[0]}) )"
                query_conditions.append(f"({final_eggs_conditions})")
            
            elif len(egg_groups)==1:
                egg_groups = egg_groups[0].capitalize()
                try:
                    query_conditions.append(f"(eggGroupID_1 == {int(egg_groups)} OR eggGroupID_2 == {int(egg_groups)})")                
                except ValueError:
                    query_conditions.append(f"(primaryEggGroup, == \"{egg_groups}\" OR secondaryEggGroup == \"{egg_groups}\")")
            
            elif len(egg_groups)>2:
                abort(400,)
        
        if ability_filter:
            if len(ability_filter)>1:
                abort(400)
            elif len(ability_filter)==1:
                try:
                    query_conditions.append(f"(AbilityId_1 == {int(ability_filter)} OR AbilityId_2 == {int(ability_filter)} OR AbilityId_3 == {int(ability_filter)})")
                except ValueError:
                    ability_filter = ability_filter.capitalize()
                    query_conditions.append(f"(primaryAbility == \"{ability_filter}\" OR secondaryAbility == \"{ability_filter}\" OR hiddenAbility == \"{ability_filter}\")")
            
            if region_filter:
                try:
                    # Do the same with the region filters.
                    query_conditions.append(f"(regionID == {int(region_filter)})")
                except ValueError:
                    query_conditions.append(f"(Region == \"{region_filter.capitalize()}\")")
                    
            if game_filter:
                try:
                    # Do the same with the game filters.
                    query_conditions.append(f"(gameID == {int(game_filter)})")
                except ValueError:
                    query_conditions.append(f"(gameOfOrigin == \"{game_filter.capitalize()}\")")
        
        query_conditions = "WHERE " + " AND ".join(query_conditions)
        pokemon_list = get_pokemon_data(query_condition=query_conditions) 
    return pokemon_list


@app.route("/pokemons/id/<db_id>")
def get_pokemon_by_id(db_id):
    db_id = int(db_id)
    query_condition = f"WHERE pokemonID == {db_id}"
    pokemon_list = get_pokemon_data(query_condition=query_condition)[0]
    return pokemon_list
    
    
@app.route("/pokemons/<pokedex_ref>")
def get_pokemon_by_pokedex(pokedex_ref):
    try:        
        pokedex_ref = int(pokedex_ref)
        query_condition = f"WHERE PokedexNumber == {pokedex_ref}"
    except ValueError:
        pokemon_name = str(pokedex_ref).lower().capitalize()
        query_condition = f"WHERE PokemonName == \"{pokemon_name}\";"
    finally:
        pokemon_list = get_pokemon_data(query_condition=query_condition)
        return pokemon_list



def get_pokemon_data(query_condition: str = "") -> list:
    query = f"""SELECT Pokemon.*,
         t1.Type as primary_type,
         t2.Type as secondary_type, 
         a1.RecordID as abilityID_1,
         a1.Ability as primary_ability, 
         a1.description as primary_ability_description, 
         a2.RecordID as abilityID_2,
         a2.Ability as secondary_ability, 
         a2.description as secondary_ability_description, 
         a3.RecordID as hidden_abilityID,
         a3.Ability as hidden_ability,
         a3.description as hidden_ability_description, 
         "Region of Origin" as region_of_origin,
         e1."Egg Group" as primary_egg_group,
         e2."Egg Group" as secondary_egg_group,
         "Game(s) of Origin" as game_of_origin
        From Pokemon
            left JOIN Types t1 ON PrimaryType == t1.RecordID 
            left JOIN Types t2 ON SecondaryType == t2.RecordID 
            LEFT JOIN Abilities a1 on PrimaryAbility == a1.RecordID
            LEFT JOIN Abilities a2 on SecondaryAbility == a2.RecordID
            LEFT JOIN Abilities a3 on HiddenAbility == a3.RecordID
            LEFT JOIN Regions on RegionofOrigin == Regions.RecordID
            LEFT JOIN EggGroups e1 on PrimaryEggGroup == e1.RecordID
            LEFT JOIN EggGroups e2 on SecondaryEggGroup == e2.RecordID
            LEFT JOIN Games on GameofOrigin == Games.RecordID
        {query_condition}
        """
    with sql3.connect("./pokeDB.db") as conn:
        df = pd.read_sql(query, conn)
        if len(df) < 1:
            abort(404, "No pokemon found with that reference")
        pokemon_found = len(df)
        df.drop(columns=["PrimaryType","SecondaryType","PrimaryAbility","SecondaryAbility", "HiddenAbility", "SpecialEventAbility", "RegionofOrigin", "GameofOrigin", "PrimaryEggGroup", "SecondaryEggGroup", ], inplace=True)
        df = df.to_dict()
        pokemon_list = []
        for i in range(pokemon_found):
            pokemon_data = {
                "id": df["PokemonID"][i],
                "Name":df["PokemonName"][i],
                "legendaryType": df["LegendaryType"][i],
                "originalPokemonID": df["OriginalPokemonID"][i],
                "alternateForm": df["AlternateFormName"][i],
                "legendaryType": df["LegendaryType"][i],
                "pokedexInfo":{
                    "pokedexNumber": df["PokedexNumber"][i],
                    "category": df["Classification"][i],
                    "height":df["PokemonHeight"][i],
                    "weight": df["PokemonWeight"][i],
                    "gameOfOrigin": df["game_of_origin"][i],
                    "regionOfOrigin": df["region_of_origin"][i],
                    "types": {
                        "primary":df["primary_type"][i],
                        "secondary":df["secondary_type"][i]    
                    },
                    "abilities": {
                        "primary": {
                            "id": df["abilityID_1"][i],
                            "ability": df["primary_ability"][i],
                            "description": df["primary_ability_description"][i]
                        },
                        "secondary": {
                            "id": df["abilityID_2"][i],
                            "ability": df["secondary_ability"][i],
                            "description": df["secondary_ability_description"][i]
                        },
                        "hidden": {
                            "id": df["hidden_abilityID"][i],
                            "ability": df["hidden_ability"][i],
                            "description": df["hidden_ability_description"][i]
                        },                  
                    }
                },               
                "training":{
                    "catchRate": df["CatchRate"][i],
                    "baseHappiness": df["BaseHappiness"][i],
                    "evolutionInfo": {
                        "previousEvolutionID": df["PreEvolutionPokemonId"][i],
                        "experienceGrowthTotal": df["ExperienceGrowthTotal"][i],
                        "evolutionDetails": df["EvolutionDetails"][i],
                        "experienceYield": df["EvolutionDetails"][i],
                    },
                    "evYield": {
                        "health": df["HealthEV"][i],
                        "attack": df["AttackEV"][i],
                        "defense": df["DefenseEV"][i],
                        "spAttack": df["SpecialAttackEV"][i],
                        "spDefense": df["SpecialDefenseEV"][i],
                        "speed": df["SpeedEV"][i],
                    },
                    "catchRate": df["CatchRate"][i],                    
                },
                "baseStats": {
                    "health": df["HealthStat"][i],
                    "attack": df["AttackStat"][i],
                    "defense": df["DefenseStat"][i],
                    "spAttack": df["SpecialAttackStat"][i],
                    "spDefense": df["SpecialDefenseStat"][i],
                    "speed": df["SpeedStat"][i],
                },
                "breeding":{
                    "eggCycleCount": df["EggCycleCount"][i],
                    "femaleRatio": df["FemaleRatio"][i],
                    "maleRatio": df["MaleRatio"][i],
                    "eggGroup": {
                        "primary": df["primary_egg_group"][i],
                        "secondary": df["secondary_egg_group"][i]
                    }
                },
            }        
             
            pokemon_list.append(pokemon_data)
    return pokemon_list
    
if __name__ == "__main__":
    app.run(debug=True)
