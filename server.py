import os
import io
import csv
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from nbt import nbt

app = FastAPI()

WORLD_DIR = os.getenv("WORLD_DIR", "/mnt/ssd/docker-data/mc/gtnh/World")
PLAYERDATA_DIR = os.path.join(WORLD_DIR, "playerdata")
LEVEL_DAT = os.path.join(WORLD_DIR, "level.dat")

# --- EMBEDDED CSV DATA ---
CSV_T1 = """
,"GregTech New Horizons - Spice of Life Tracker, T1 (Raw)",,,,,,,,,,,,,,,,,,,,,,,
,68,Shanks Obtained (Out of 331),,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,
,Pam's HarvestCraft,,,102,,Extra Trees,,,80,,Vanilla,,,9,,Meats and Fish,,,49,,Mob Drops,,,9
,TRUE,Almond (Pam),,1,,FALSE,Acorn,,1,,TRUE,Apple,,1,,TRUE,Clownfish,,1,,FALSE,Blaze Flesh,,2
,FALSE,Apricot (Pam),,1,,FALSE,Allspice,,1,,TRUE,Carrot,,1,,FALSE,Green Heart Fish,,1,,FALSE,Coagulated Blood,,1
,TRUE,Artichoke,,1,,FALSE,Almond (ET),,1,,FALSE,Chorus Fruit,,2,,FALSE,Pufferfish,,1,,FALSE,Gelatinous Slime,,1
,FALSE,Asparagus,,1,,FALSE,Apricot (ET),,2,,FALSE,Glow Berries,,1,,FALSE,Raw Anchovy,,1,,FALSE,Gluttony Shard,,1
,FALSE,Avocado (Pam),,1,,FALSE,Avacado (ET),,1,,FALSE,Melon Slice,,1,,FALSE,Raw Bass,,1,,FALSE,Rotten Flesh,,1
,TRUE,Bamboo Shoot,,1,,FALSE,Banana (ET),,2,,TRUE,Poisonous Potato,,1,,FALSE,Raw Beef,,1,,FALSE,Spider Eye,,1
,TRUE,Banana (Pam),,1,,FALSE,Beechnut,,1,,TRUE,Potato,,1,,FALSE,Raw Calamari,,1,,FALSE,Zombie Brain,,2
,FALSE,Barley,,1,,FALSE,Black Cherry,,1,,TRUE,Sweet Berries,,1,,FALSE,Raw Carp,,1,,,,,
,FALSE,Beans,,1,,FALSE,Blackthorn,,2,,,,,,,FALSE,Raw Catfish,,1,,Twilight Forest,,,27
,FALSE,Beet,,1,,FALSE,Blackberry (ET),,1,,Biomes of Plenty,,,12,,FALSE,Raw Charr,,1,,FALSE,Experiment 115,,2
,TRUE,Bellpepper,,1,,FALSE,Blackcurrant,,1,,TRUE,Berry,,1,,TRUE,Raw Chicken,,1,,FALSE,Hydra Chop,,9
,TRUE,Blackberry (Pam),,1,,FALSE,Blueberry (ET),,1,,FALSE,Bowl of Rice,,1,,FALSE,Raw Clam,,1,,FALSE,Maze Wafer,,2
,TRUE,Blueberry (Pam),,1,,FALSE,Brazil Nut,,1,,FALSE,Peach (BoP),,3,,TRUE,Raw Cod,,1,,FALSE,Meef Steak,,3
,TRUE,Broccoli,,1,,FALSE,Buddhas Hand,,2,,FALSE,Pear (BoP),,3,,FALSE,Raw Crab,,1,,FALSE,Meef Stroganoff,,4
,TRUE,Brussel Sprout,,1,,FALSE,Butternut,,1,,FALSE,Persimmon (BoP),,1,,FALSE,Raw Crayfish,,1,,FALSE,Raw Meef,,1
,TRUE,Cabbage,,1,,FALSE,Candlenut,,1,,FALSE,Shroom Powder,,1,,FALSE,Raw Eel,,1,,FALSE,Raw Venison (TF),,2
,TRUE,Cactus Fruit,,1,,FALSE,Cashew (ET),,1,,FALSE,Turnip (BoP),,1,,FALSE,Raw Frog,,1,,FALSE,Venison Steak,,4
,TRUE,Candleberry,,1,,FALSE,Cherry Plum,,2,,TRUE,Wild Carrots,,1,,FALSE,Raw Grouper,,1,,,,,
,FALSE,Cantaloupe,,2,,FALSE,Chilli (ET),,1,,,,,,,FALSE,Raw Herring,,1,,,,,
,TRUE,Cashew (Pam),,1,,FALSE,Citron,,2,,Forestry,,,7,,FALSE,Raw Horse Meat,,1,,,,,
,TRUE,Cauliflower,,1,,FALSE,Clove,,1,,FALSE,Cherry (Forestry),,1,,FALSE,Raw Human Meat,,1,,,,,
,TRUE,Celery,,1,,FALSE,Coconut (ET),,1,,FALSE,Chestnut (Forestry),,1,,FALSE,Raw Imphide,,2,,,,,
,TRUE,Cherry (Pam),,1,,FALSE,Coffee (ET),,1,,FALSE,Date (Forestry),,1,,FALSE,Raw Jellyfish,,1,,,,,
,TRUE,Chestnut (Pam),,1,,FALSE,Crabapple,,1,,FALSE,Lemon (Forestry),,1,,FALSE,Raw Mudfish,,1,,,,,
,TRUE,Chili Pepper (Pam),,1,,FALSE,Cranberry (ET),,1,,FALSE,Papaya (Forestry),,1,,TRUE,Raw Mutton,,1,,,,,
,FALSE,Cinnamon,,1,,FALSE,Elderberry,,1,,FALSE,Plum (Forestry),,1,,FALSE,Raw Ocelot Meat,,1,,,,,
,TRUE,Coconut (Pam),,1,,FALSE,Fig (ET),,1,,FALSE,Walnut (Forestry),,1,,FALSE,Raw Octopus,,1,,,,,
,TRUE,Coffee Beans,,1,,FALSE,Finger Lime,,2,,,,,,,FALSE,Raw Perch,,1,,,,,
,FALSE,Corn,,1,,FALSE,Gingko Nut,,1,,Natura,,,13,,TRUE,Raw Porkchop,,1,,,,,
,FALSE,Cranberry (Pam),,1,,FALSE,Golden Raspberry,,1,,TRUE,Blackberry (Natura),,1,,FALSE,Raw Rabbit (EFR),,2,,,,,
,TRUE,Cucumber (Pam),,1,,FALSE,Gooseberry (ET),,1,,FALSE,Blightberry,,1,,FALSE,Raw Rabbit (Pam),,1,,,,,
,TRUE,Curry Leaf,,1,,FALSE,Grapefruit (ET),,2,,TRUE,Blueberry (Natura),,1,,FALSE,Raw Salmon,,1,,,,,
,FALSE,Date (Pam),,1,,FALSE,Hazelnut,,1,,FALSE,Cactus Juice,,1,,FALSE,Raw Scallop,,1,,,,,
,FALSE,Dragonfruit,,1,,FALSE,Juniper,,1,,FALSE,Duskberry,,1,,FALSE,Raw Shrimp,,1,,,,,
,TRUE,Durian,,1,,FALSE,Key Lime,,1,,TRUE,Maloberry,,1,,FALSE,Raw Snail,,1,,,,,
,FALSE,Edible Root,,1,,FALSE,Kumquat,,1,,FALSE,Potash Apple,,2,,FALSE,Raw Snapper,,1,,,,,
,TRUE,Eggplant,,1,,FALSE,Lime (ET),,1,,TRUE,Raspberry (Natura),,1,,FALSE,Raw Tilapia,,1,,,,,
,FALSE,Fig (Pam),,1,,FALSE,Manderin,,2,,FALSE,Saguaro Fruit,,2,,FALSE,Raw Trout,,1,,,,,
,FALSE,Flesh Root,,1,,FALSE,Mango (ET),,2,,FALSE,Skyberry,,1,,FALSE,Raw Tuna,,1,,,,,
,TRUE,Garlic,,1,,FALSE,Nectarine,,2,,FALSE,Stingberry,,1,,FALSE,Raw Turkey,,1,,,,,
,FALSE,Ginger,,1,,FALSE,Nutmeg (ET),,1,,,,,,,FALSE,Raw Turtle,,1,,,,,
,TRUE,Gooseberry (Pam),,1,,FALSE,Olive (ET),,1,,Galacticraft,,,2,,FALSE,Raw Venison (Pam),,2,,,,,
,TRUE,Grape,,1,,FALSE,Orange (ET),,2,,FALSE,Cheese Curd,,1,,FALSE,Raw Walleye,,1,,,,,
,FALSE,Grapefruit (Pam),,1,,FALSE,Osange Orange,,1,,FALSE,Unknown Fruits,,1,,FALSE,Raw Wolf Meat,,1,,,,,
,FALSE,Honey,,2,,FALSE,Papayimar,,4,,,,,,,FALSE,Unidentifiable Meat,,2,,,,,
,FALSE,Ignis Fruit,,1,,FALSE,Peach (ET),,2,,IC2 Crops,,,14,,,,,,,,,,
,TRUE,Kiwi,,1,,FALSE,Pear (ET),,2,,FALSE,Chilly Pepper (GT),,1,,,,,,,,,,
,TRUE,Leek,,1,,FALSE,Pecan Nut,,1,,FALSE,Cucumber (GT),,1,,,,,,,,,,
,FALSE,Lemon (Pam),,1,,FALSE,Plantain,,1,,FALSE,Goldfish,,1,,,,,,,,,,
,TRUE,Lettuce,,1,,FALSE,Pomelo,,2,,FALSE,Grapes (GT),,1,,,,,,,,,,
,FALSE,Lime (Pam),,1,,FALSE,Raspberry (ET),,1,,FALSE,Huckleberry,,1,,,,,,,,,,
,TRUE,Mango (Pam),,1,,FALSE,Red Banana,,1,,FALSE,Lemon (GT),,1,,,,,,,,,,
,FALSE,Maple Syrup,,1,,FALSE,Redcurrant,,1,,FALSE,Max Tomato,,5,,,,,,,,,,
,FALSE,Marrow Berry,,1,,FALSE,Sand Pear,,1,,FALSE,Onion (GT),,1,,,,,,,,,,
,TRUE,Mustard Seeds,,1,,FALSE,Satsuma,,2,,FALSE,Sugar Beet,,1,,,,,,,,,,
,TRUE,Nutmeg (Pam),,1,,FALSE,Sour Cherry,,1,,FALSE,Tomato (GT),,1,,,,,,,,,,
,FALSE,Oats,,1,,FALSE,Star Anise,,1,,,,,,,,,,,,,,,
,TRUE,Okra,,1,,FALSE,Starfruit (ET),,1,,GregTech,,,7,,,,,,,,,,
,TRUE,Olive (Pam),,1,,FALSE,Tangerine,,2,,FALSE,Cheese (GT),,2,,,,,,,,,,
,FALSE,Onion (Pam),,1,,FALSE,Wild Cherry,,1,,FALSE,Cheese Slice,,1,,,,,,,,,,
,TRUE,Orange (Pam),,1,,,,,,,FALSE,Cucumber Slice,,1,,,,,,,,,,
,TRUE,Papaya (Pam),,1,,,,,,,FALSE,Lemon Slice,,1,,,,,,,,,,
,FALSE,Parsnip,,1,,,,,,,FALSE,Onion Slice,,1,,,,,,,,,,
,FALSE,Peach (Pam),,1,,,,,,,FALSE,Tomato Slice,,1,,,,,,,,,,
,TRUE,Peanut,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Pear (Pam),,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Peas,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Pecan,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Peppercorn,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Persimmon (Pam),,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Pineapple,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Pistachio,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Plum (Pam),,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Pomegranate,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Radish,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Raspberry (Pam),,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Rhubarb,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Rice,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Rutabaga,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Rye,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Scallion,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Seaweed,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Sesame Seeds,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Soybean,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Spice Leaf,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Spinach,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Starfruit (Pam),,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Strawberry,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Sunflower Seeds,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Sweet Potato,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Tea Leaf,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Tomato (Pam),,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Turnip (Pam),,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Vanilla Bean,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Walnut (Pam),,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Water Chestnut,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,White Mushroom,,1,,,,,,,,,,,,,,,,,,,,
,TRUE,Winter Squash,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Zucchini,,1,,,,,,,,,,,,,,,,,,,,
"""

CSV_T2 = """
,"GregTech New Horizons - Spice of Life Tracker, T2 (Basic)",,,,,,,,,,,,,,,,,,,,,,,,,,,,
,30,Shanks Obtained (Out of 660),,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,Basic Meals,,,277,,Cooked Crops,,,23,,Juices and Milks,,,65,,Smoothies,,,83,,Jellies,,,53,,Yogurts,,,68
,FALSE,Apple Cider,,3,,TRUE,Baked Potato,,2,,FALSE,Apple Juice (Pam),,2,,FALSE,Apple Smoothie,,3,,FALSE,Apple Jelly,,2,,FALSE,Apple Yogurt,,2
,FALSE,Apple Sauce,,2,,FALSE,Baked Sweet Potato,,2,,FALSE,Apricot Juice,,2,,FALSE,Apricot Smoothie,,3,,FALSE,Apricot Jelly,,2,,FALSE,Apricot Yogurt,,2
,FALSE,Apricot Glazed Pork,,4,,FALSE,Cup of Coffee,,2,,FALSE,Banana Juice,,3,,FALSE,Banana Smoothie,,3,,FALSE,Blackberry Jelly,,2,,FALSE,Banana Yogurt,,2
,FALSE,Bacon Wrapped Dates,,4,,FALSE,Cup of Tea,,2,,FALSE,Blackberry Juice,,2,,FALSE,Blackberry Smoothie,,3,,FALSE,Blueberry Jelly,,2,,TRUE,Blackberry Yogurt,,2
,FALSE,Baked Ham,,5,,FALSE,Grilled Asparagus,,2,,FALSE,Blueberry Juice,,2,,FALSE,Blueberry Smoothie,,3,,FALSE,Cherry Jelly,,2,,FALSE,Blueberry Yogurt,,2
,FALSE,Bamboo Steamed Rice,,4,,FALSE,Grilled Eggplant,,2,,FALSE,Cactus Fruit Juice,,2,,FALSE,Cherry Smoothie,,3,,FALSE,Cranberry Jelly,,2,,FALSE,Cherry Yogurt,,2
,FALSE,Breaded Porkchop,,4,,FALSE,Grilled Mushroom,,2,,FALSE,Carrot Juice,,2,,FALSE,Coconut Smoothie,,3,,FALSE,Fig Jelly,,2,,FALSE,Chocolate Yogurt,,2
,FALSE,California Roll,,4,,FALSE,Popcorn,,2,,FALSE,Cherry Juice,,2,,FALSE,Cranberry Smoothie,,3,,FALSE,Gooseberry Jelly,,3,,FALSE,Coconut Yogurt,,2
,FALSE,Candied Ginger,,2,,FALSE,Raisins,,2,,FALSE,Chocolate Milk (Pam),,2,,FALSE,Fig Smoothie,,3,,FALSE,Grape Jelly,,2,,FALSE,Cranberry Yogurt,,4
,FALSE,Candied Lemon,,2,,FALSE,Roasted Chestnut,,2,,FALSE,Coconut Milk,,2,,FALSE,Gooseberry Smoothie,,3,,FALSE,Grapefruit Jelly,,2,,FALSE,Fig Yogurt,,2
,FALSE,Candied Sweet Potatoes,,3,,FALSE,Roasted Pumpkin Seeds,,1,,FALSE,Cranberry Juice,,2,,FALSE,Grape Smoothie,,3,,FALSE,Kiwi Jelly,,2,,FALSE,Gooseberry Yogurt,,4
,FALSE,Candied Walnuts,,4,,FALSE,Toasted Coconut,,2,,FALSE,Fig Juice,,2,,FALSE,Grapefruit Smoothie,,3,,FALSE,Lemon Jelly,,2,,FALSE,Grape Yogurt,,2
,FALSE,Caramel,,1,,,,,,,FALSE,Fruit Punch,,2,,FALSE,Kiwi Smoothie,,3,,FALSE,Lime Jelly,,2,,FALSE,Grapefruit Yogurt,,2
,FALSE,Caramel Apple,,3,,Cooked Meats,,,57,,FALSE,Gooseberry Juice,,3,,FALSE,Lemon Smoothie,,3,,FALSE,Mango Jelly,,2,,TRUE,Kiwi Yogurt,,2
,TRUE,Celery and Peanut Butter,,3,,FALSE,Boiled Egg,,1,,FALSE,Grape Juice (Pam),,2,,FALSE,Lime Smoothie,,3,,FALSE,Orange Jelly,,2,,FALSE,Lemon Yogurt,,2
,FALSE,Chai Tea,,2,,FALSE,Cooked Calamari,,2,,FALSE,Grapefruit Juice,,2,,FALSE,Mango Smoothie,,3,,FALSE,Papaya Jelly,,2,,FALSE,Lime Yogurt,,2
,FALSE,Chili Poppers,,4,,FALSE,Cooked Clam,,1,,FALSE,Kiwi Juice,,2,,FALSE,Melon Smoothie,,3,,FALSE,Peach Jelly,,2,,FALSE,Mango Yogurt,,2
,FALSE,Chorizo,,5,,FALSE,Cooked Cod,,2,,FALSE,Lemonade (Pam),,1,,FALSE,Orange Smoothie,,3,,FALSE,Pear Jelly,,3,,FALSE,Melon Yogurt,,2
,FALSE,Cinnamon Apple Oatmeal,,6,,FALSE,Cooked Crab,,1,,FALSE,Lime Juice,,2,,FALSE,Papaya Smoothie,,3,,FALSE,Persimmon Jelly,,2,,FALSE,Orange Yogurt,,2
,FALSE,Coconut Cream,,1,,FALSE,Cooked Crayfish,,1,,FALSE,Mango Juice,,2,,FALSE,Peach Smoothie,,3,,FALSE,Plum Jelly,,3,,FALSE,Papaya Yogurt,,2
,FALSE,Coffee con Leche,,2,,FALSE,Cooked Frog Legs,,1,,FALSE,Melon Juice,,2,,FALSE,Pear Smoothie,,3,,FALSE,Pomegranate Jelly,,2,,FALSE,Peach Yogurt,,2
,FALSE,Cornflakes,,4,,FALSE,Cooked Horse Meat,,2,,FALSE,Orange Juice,,2,,FALSE,Persimmon Smoothie,,3,,FALSE,Raspberry Jelly,,2,,FALSE,Pear Yogurt,,2
,FALSE,Cracker,,2,,FALSE,Cooked Human Meat,,2,,FALSE,Papaya Juice,,2,,FALSE,Pinacolada,,2,,FALSE,Starfruit Jelly,,2,,FALSE,Persimmon Yogurt,,2
,FALSE,Cranberry Sauce,,2,,FALSE,Cooked Imphide,,4,,FALSE,Peach Juice,,2,,FALSE,Plum Smoothie,,3,,FALSE,Strawberry Jelly,,2,,FALSE,Pineapple Yogurt,,2
,FALSE,"Enderios",,5,,TRUE,Cooked Mutton,,2,,FALSE,Pear Juice,,2,,FALSE,Pomegranate Smoothie,,3,,FALSE,Watermelon Jelly,,2,,FALSE,Plain Yogurt,,2
,FALSE,Espresso,,1,,FALSE,Cooked Ocelot Meat,,2,,FALSE,Persimmon Juice,,2,,FALSE,Raspberry Smoothie,,3,,,,,,,FALSE,Plum Yogurt,,2
,FALSE,Fish Lettuce Wrap,,4,,FALSE,Cooked Octopus,,1,,FALSE,Plum Juice,,2,,FALSE,Starfruit Smoothie,,3,,Basic Cooking Ingredients,,,22,,FALSE,Pomegranate Yogurt,,2
,FALSE,Fish Sticks,,4,,FALSE,Cooked Porkchop,,2,,FALSE,Pomegranate Juice,,2,,FALSE,Strawberry Smoothie,,3,,FALSE,Almond Butter,,3,,FALSE,Pumpkin Yogurt,,2
,FALSE,Fried Onions,,2,,TRUE,Cooked Rabbit (EFR),,3,,FALSE,Raspberry Juice,,2,,,,,,,FALSE,Cashew Butter,,3,,FALSE,Raspberry Yogurt,,2
,FALSE,Fried Pecan Okra,,3,,FALSE,Cooked Rabbit (Pam),,3,,FALSE,Soy Milk,,2,,Milkshakes,,,12,,FALSE,Cheese (Pam),,1,,FALSE,Starfruit Yogurt,,2
,FALSE,Futo Maki,,5,,FALSE,Cooked Salmon,,3,,FALSE,Starfruit Juice,,2,,TRUE,Banana Milkshake,,3,,FALSE,Chestnut Butter,,3,,FALSE,Strawberry Yogurt,,2
,FALSE,Garlic Chicken,,7,,FALSE,Cooked Scallop,,1,,FALSE,Strawberry Juice,,2,,FALSE,Chocolate Milkshake,,3,,FALSE,Firm Tofu,,2,,FALSE,Vanilla Yogurt,,2
,FALSE,Gherkin,,3,,FALSE,Cooked Shrimp,,1,,,,,,,FALSE,Gooseberry Milkshake,,3,,FALSE,Peanut Butter,,2,,,,,
,FALSE,Ginger Chicken,,6,,FALSE,Cooked Snail,,1,,,,,,,FALSE,Strawberry Milkshake,,3,,FALSE,Pistachio Butter,,3,,,,,
,FALSE,Gravy,,2,,FALSE,Cooked Turkey,,3,,,,,,,,,,,,FALSE,Silken Tofu,,3,,,,,
,FALSE,Grilled Skewer,,5,,FALSE,Cooked Turtle,,1,,,,,,,,,,,,TRUE,Stock,,2,,,,,
,FALSE,Gummy Bears,,2,,FALSE,Cooked Venison,,4,,,,,,,,,,,,,,,,,,,,
,FALSE,Honey Lemon Lamb,,4,,FALSE,Cooked Wolf Meat,,2,,,,,,,,,,,,,,,,,,,,
,FALSE,Hot Chocolate (Pam),,2,,FALSE,Fried Egg,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Jellybeans,,1,,FALSE,Scrambled Egg,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Kimchi,,5,,TRUE,Steak,,2,,,,,,,,,,,,,,,,,,,,
,FALSE,Lamb Kebab,,6,,FALSE,Unidentifiable Cooked Meat,,4,,,,,,,,,,,,,,,,,,,,
,FALSE,Mango Chutney,,3,,FALSE,Unidentifiable Meat Nugget,,1,,,,,,,,,,,,,,,,,,,,
,FALSE,Manjuu,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Maple Candied Bacon,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Maple Oatmeal,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Maple Sausage,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Marinated Cucumbers,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Marshmellows,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Marzipan,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Mochi,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Okra Chips,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Omelet,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Peaches and Cream Oatmeal,,6,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Peppermint,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pepperoni,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pickled Beets,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pickled Onions,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pickles,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pineapple Ham,,6,,,,,,,,,,,,,,,,,,,,,,,,,,,
,TRUE,Pistachio Baked Salmon,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Poached Pear,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pork Lettuce Wrap,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pork Sausage,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Pralines,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Raspberry Iced Tea,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Roast Chicken,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Salted Sunflower Seeds,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sausage,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Scallion Baked Potato,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sesame Ball,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sesame Snaps,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Steamed Spinach,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Stuffed Eggplant,,6,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Stuffed Pepper,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,
,TRUE,Suadero,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sushi,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sweet Pickle,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Sweetwart,,1,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Taffy,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Vegemite,,2,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Vegetarian Lettuce Wrap,,4,,,,,,,,,,,,,,,,,,,,,,,,,,,
,FALSE,Veggie Strips,,3,,,,,,,,,,,,,,,,,,,,,,,,,,,
"""

CSV_T3 = """
,"GregTech New Horizons - Spice of Life Tracker, T3 (Intermediate)",,,,,,,,,,,,,,,,,,,,,,,
,44,Shanks Obtained (Out of 627),,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,
,Intermediate Meals,,,241,,Bread Stuff,,,50,,Pies,,,121,,Pizzas,,,40,,Cookies and Muffins,,,37
,FALSE,Asparagus Quiche,,5,,FALSE,Baguette,,4,,FALSE,Apple Pie,,5,,FALSE,Cheese Pizza,,2,,FALSE,Biscuit of Totality,,1
,FALSE,Banana Nut Bread,,5,,TRUE,Baguettes,,4,,FALSE,Blackberry Cobbler,,5,,FALSE,Meat Feast Pizza,,9,,FALSE,Blood Cookie,,1
,FALSE,Banana Split,,7,,FALSE,Bread,,3,,FALSE,Blueberry Pie,,6,,FALSE,Mince Meat Pizza,,3,,FALSE,Blueberry Muffin,,4
,FALSE,Battered Sausage,,5,,FALSE,Breads,,3,,FALSE,Cherry Pie,,6,,FALSE,Pizza,,8,,FALSE,Chaos Cookie,,2
,FALSE,Blueberry Pancakes,,6,,FALSE,Bun,,2,,FALSE,Chicken Pot Pie,,8,,FALSE,Raw Cheese Pizza,,1,,TRUE,Cookie,,1
,FALSE,Chicken Parmesan,,5,,FALSE,Buns,,2,,FALSE,Cottage Pie,,6,,FALSE,Raw Mince Meat Pizza,,1,,FALSE,Cream Cookie,,6
,FALSE,Chiko Roll,,7,,FALSE,Cheese on Toast,,4,,FALSE,Fruit Crumble,,6,,FALSE,Raw Veggie Pizza,,1,,FALSE,Ginger Snaps,,2
,FALSE,Cinnamon Roll,,5,,FALSE,Chocolate Dough,,1,,FALSE,Gingered Rhubarb Tart,,4,,FALSE,Supreme Pizza,,12,,FALSE,Juice and Cookies,,3
,FALSE,Coconut Shrimp,,6,,FALSE,Cookie shaped Dough,,1,,FALSE,Gooseberry Pie,,4,,FALSE,Veggie Pizza,,2,,FALSE,Lavender Shortbread,,4
,FALSE,Cornbread,,5,,FALSE,Dough (GT),,1,,FALSE,Keylime Pie,,7,,,,,,,FALSE,Peanut Butter Cookies,,3
,FALSE,Cornish Pasty,,6,,FALSE,Dough in Baguette Shape,,1,,FALSE,Lemon Meringue,,6,,,,,,,FALSE,Pumpkin Muffin,,4
,FALSE,Cranberry Bar,,5,,FALSE,Dough in Bread Shape,,1,,FALSE,Meat Pie,,7,,Ice Creams,,,45,,FALSE,Pumpkin Oat Scones,,3
,FALSE,Custard,,5,,FALSE,Dough in Bun Shape,,1,,FALSE,Mince Pie,,6,,FALSE,Caramel Ice Cream,,4,,TRUE,Raisin Cookies,,3
,FALSE,Date Nut Bread,,5,,FALSE,Sliced Baguette,,2,,FALSE,Peach Cobbler,,6,,FALSE,Cherry Ice Cream,,5,,,,,
,FALSE,Dim Sum,,6,,FALSE,Sliced Bread,,1,,FALSE,Pecan Pie,,7,,FALSE,Chocolate Ice Cream (Pam),,3,,Donuts,,,29
,FALSE,Egg Nog,,2,,FALSE,Sliced Bun,,1,,FALSE,Pumpkin Pie,,3,,FALSE,Ice Cream,,2,,FALSE,Chocolate Donut,,5
,FALSE,Fig Bar,,4,,FALSE,Sugary Dough,,1,,FALSE,Raspberry Pie,,6,,FALSE,Mint Chocolate Chip Ice Cream,,5,,FALSE,Cinnamon Sugar Donut,,5
,FALSE,Fish and Chips,,8,,FALSE,Toast (Pam),,4,,FALSE,Shepherd's Pie,,6,,FALSE,Mocha Ice Cream,,3,,FALSE,Donut,,4
,FALSE,Fish Dinner,,6,,FALSE,Toast Sandwich,,6,,FALSE,Spinach Pie,,4,,FALSE,Neapolitan Ice Cream,,5,,FALSE,Frosted Donut,,5
,FALSE,French Toast,,7,,FALSE,Tortilla,,3,,TRUE,Strawberry Pie,,6,,FALSE,Pistachio Ice Cream,,5,,FALSE,Jelly Donut,,5
,TRUE,Fried Chicken,,7,,FALSE,Toast (Cooking for BH),,4,,TRUE,Sweet Potato Pie,,7,,FALSE,Spumoni Ice Cream,,5,,FALSE,Powdered Donut,,5
,FALSE,Ginger Bread,,6,,,,,,,,,,,,FALSE,Strawberry Ice Cream,,4,,,,,
,FALSE,Golden Apple (Blocks),,2,,Potato Stuff,,,28,,Cakes,,,21,,FALSE,Vanilla Ice Cream,,4,,,,,
,FALSE,Golden Apple (Ingots),,2,,FALSE,Bag of Chili Chips,,4,,FALSE,Baked Cake Bottom,,2,,,,,,,,,,
,FALSE,Golden Carrot,,3,,FALSE,Bag of Potato Chips,,4,,FALSE,Blood Cake,,1,,,,,,,,,,
,FALSE,Golden Head,,2,,FALSE,Chili Chips,,4,,FALSE,Cake,,1,,,,,,,,,,
,FALSE,Hushpuppies,,3,,FALSE,Fries (Pam),,3,,FALSE,Cake Bottom,,1,,,,,,,,,,
,FALSE,Lamb with Mint Sauce,,6,,FALSE,Potato Chips (GT),,4,,TRUE,Carrot Cake,,1,,,,,,,,,,
,FALSE,Lemon Bar,,2,,FALSE,Potato Chips (Raw),,1,,TRUE,Cheese Cake,,1,,,,,,,,,,
,FALSE,Maple Syrup Pancakes,,6,,FALSE,Potato on a Stick,,1,,TRUE,Cherry Cheese Cake,,1,,,,,,,,,,
,FALSE,Naan,,3,,FALSE,Potato Strips,,1,,TRUE,Chocolate Sprinkles Cake,,1,,,,,,,,,,
,FALSE,Pancakes,,4,,FALSE,Roast Potatoes,,3,,FALSE,Holiday Cake,,1,,,,,,,,,,
,FALSE,Paneer,,2,,FALSE,Roasted Potato on a Stick,,3,,FALSE,Lamington,,1,,,,,,,,,,
,FALSE,Potato and Cheese Pirogi,,5,,,,,,,FALSE,Nethercake,,3,,,,,,,,,,
,FALSE,Pumpkin Bread,,5,,Jerkies,,,15,,FALSE,Pavlova,,1,,,,,,,,,,
,FALSE,Raspberry Trifle,,4,,FALSE,Bacon Jerky,,1,,TRUE,Pineapple Upside Down Cake,,1,,,,,,,,,,
,FALSE,Salmon Patties,,6,,TRUE,Beef Jerky (Pam),,3,,TRUE,Pumpkin Cheese Cake,,1,,,,,,,,,,
,FALSE,Sausage Roll,,5,,FALSE,Beef Jerky (TiC),,1,,FALSE,Red Velvet Cake,,1,,,,,,,,,,
,FALSE,Shrimp Pork Okra Hushpuppies,,5,,TRUE,Brain Jerky,,3,,FALSE,Rice Cake,,2,,,,,,,,,,
,FALSE,Spice Bun,,4,,FALSE,Chicken Jerky,,1,,FALSE,Thaumic Cake,,1,,,,,,,,,,
,FALSE,Spicy Mustard Pork,,5,,FALSE,Coagulated Blood Drop,,1,,,,,,,,,,,,,,,
,FALSE,Steak and Chips,,6,,FALSE,Fish Jerky,,1,,,,,,,,,,,,,,,
,FALSE,Stuffed Mushroom,,6,,FALSE,Gelatinous Slime Drop,,1,,,,,,,,,,,,,,,
,FALSE,Sunflower Wheat Rolls,,6,,FALSE,Monster Jerky,,1,,,,,,,,,,,,,,,
,FALSE,Vegemite on Toast,,4,,FALSE,Mutton Jerky,,1,,,,,,,,,,,,,,,
,FALSE,Walnut Raisin Bread,,5,,FALSE,Zombie Jerky,,1,,,,,,,,,,,,,,,
,TRUE,Zeppole,,4,,,,,,,,,,,,,,,,,,,,
,FALSE,Zucchini Bread,,5,,,,,,,,,,,,,,,,,,,,
,FALSE,Zucchini Fries,,8,,,,,,,,,,,,,,,,,,,,
"""

CSV_T4 = """
,"GregTech New Horizons - Spice of Life Tracker, T4 (Advanced)",,,,,,,,,,,,,,,,,,,,,,,
,107,Shanks Obtained (Out of 1264),,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,,,,,,
,Advanced Meals,,,279,,Jelly Sandwiches,,,190,,Salads,,,84,,Soups and Stews,,,184,,Chocolate,,,60
,FALSE,Baked Beets,,4,,FALSE,Apple Jelly Sandwich,,8,,FALSE,Beet Salad,,4,,FALSE,Asparagus Soup,,4,,FALSE,Cherry Coconut Chocolate Bar,,5
,FALSE,Baked Turnips,,5,,FALSE,Apricot Jelly Sandwich,,8,,TRUE,Berry Medley,,3,,FALSE,Beet Soup,,4,,FALSE,Chili Chocolate,,2
,FALSE,Baklava,,7,,FALSE,Blackberry Jelly Sandwich,,8,,FALSE,Ceasar Salad,,5,,FALSE,Beetroot Soup,,3,,FALSE,Chocolate Bacon,,5
,FALSE,Bangers and Mash,,6,,FALSE,Blueberry Jelly Sandwich,,8,,FALSE,Citrus Salad,,4,,FALSE,Cactus Soup,,3,,FALSE,Chocolate Bar (Pam),,2
,TRUE,Beans on Toast,,4,,FALSE,Cherry Jelly Sandwich,,8,,FALSE,Cucumber Salad,,5,,FALSE,Carrot Soup,,4,,FALSE,Chocolate Caramel Fudge,,5
,FALSE,Beef Wellington,,16,,FALSE,Cranberry Jelly Sandwich,,8,,FALSE,Egg Salad,,3,,FALSE,Celery Soup,,4,,FALSE,Chocolate Cherry,,2
,FALSE,Biscuit,,4,,FALSE,Fig Jelly Sandwich,,8,,FALSE,Fruit Salad (BoP),,3,,FALSE,Chicken Noodle Soup,,7,,FALSE,Chocolate Roll,,4
,FALSE,Braised Onions,,4,,FALSE,Gooseberry Jelly Sandwich,,5,,FALSE,Fruit Salad (Pam),,3,,FALSE,Cream of Avocado Soup,,6,,FALSE,Chocolate Strawberry,,3
,FALSE,Brownie,,7,,FALSE,Grapefruit Jelly Sandwich,,8,,FALSE,Grape Salad,,4,,FALSE,Creamed Broccoli Soup,,5,,FALSE,Honeycomb Chocolate Bar,,4
,FALSE,Buttered Potato,,4,,FALSE,Kiwi Jelly Sandwich,,8,,FALSE,Mixed Salad,,5,,FALSE,Cucumber Soup,,4,,FALSE,Jaffa,,6
,FALSE,Corn on the Cob,,3,,FALSE,Lemon Jelly Sandwich,,8,,FALSE,Potato Salad,,4,,TRUE,Garden Soup,,4,,FALSE,Jam Roll,,4
,FALSE,Cosmic Meatballs,,10,,FALSE,Lime Jelly Sandwich,,8,,FALSE,Roasted Root Veggie Medley,,6,,FALSE,Glowshroom Stew 1,,3,,FALSE,Nutella,,4
,FALSE,Croissant,,4,,FALSE,Mango Jelly Sandwich,,8,,FALSE,Shroom Salad,,3,,FALSE,Glowshroom Stew 2,,3,,FALSE,Snickers Bar,,4
,FALSE,Damper,,4,,FALSE,Orange Jelly Sandwich,,8,,FALSE,Spicy Greens,,6,,FALSE,Glowshroom Stew 3,,3,,FALSE,Tim Tam,,5
,FALSE,Deluxe Chicken Curry,,9,,FALSE,Papaya Jelly Sandwich,,8,,FALSE,Spring Salad,,4,,FALSE,Glowshroom Stew 4,,3,,FALSE,Trail Mix,,5
,FALSE,Epic Bacon,,16,,FALSE,PB&J,,7,,TRUE,Strawberry Salad,,4,,FALSE,Glowshroom Stew 5,,3,,,,,
,FALSE,Fairy Bread,,3,,FALSE,Peach Jelly Sandwich,,8,,FALSE,Summer Radish Salad,,4,,FALSE,Lamb Barley Soup,,5,,,,,
,FALSE,Garlic Bread,,6,,FALSE,Pear Jelly Sandwich,,5,,FALSE,Summer Squash with Radish,,6,,FALSE,Leek Bacon Soup,,6,,,,,
,FALSE,Garlic Mashed Potatoes,,6,,FALSE,Persimmon Jelly Sandwich,,8,,TRUE,Sunflower Broccoli Salad,,5,,TRUE,Meaty Stew (Pam),,6,,,,,
,FALSE,Glazed Carrots,,3,,TRUE,Plum Jelly Sandwich,,5,,FALSE,Veggie Salad,,3,,FALSE,Meaty Stew (Witchery),,6,,,,,
,FALSE,Hearty Breakfast,,15,,FALSE,Pomegranate Jelly Sandwich,,8,,,,,,,FALSE,Mushroom Stew (Vanilla),,2,,,,,
,TRUE,Hot Wings,,5,,FALSE,Raspberry Jelly Sandwich,,8,,Bowls,,,204,,FALSE,Mushroom Stew 1 (Natura),,3,,,,,
,FALSE,Jeweled Apple,,2,,FALSE,Starfruit Jelly Sandwich,,8,,FALSE,Baked Beans,,5,,FALSE,Mushroom Stew 2 (Natura),,3,,,,,
,FALSE,Lemon Chicken,,7,,FALSE,Strawberry Jelly Sandwich,,8,,FALSE,Beans and Rice,,7,,FALSE,Mushroom Stew 3 (Natura),,3,,,,,
,TRUE,Loaded Baked Potato,,8,,FALSE,Watermelon Jelly Sandwich,,8,,FALSE,Broccoli Mac,,7,,FALSE,Mushroom Stew 4 (Natura),,3,,,,,
,FALSE,Maple Syrup Waffles,,7,,,,,,,FALSE,Broccoli n Dip,,4,,FALSE,Mushroom Stew 5 (Natura),,3,,,,,
,FALSE,Mashed Potatoes,,5,,Sandwiches,,,263,,FALSE,Cashew Chicken,,6,,FALSE,Old World Veggie Soup,,4,,,,,
,FALSE,Mashed Sweet Potatoes,,3,,FALSE,Avocado Burrito,,7,,FALSE,Chicken Celery Casserole,,6,,FALSE,Onion Soup,,4,,,,,
,FALSE,Ploughman's Lunch,,7,,FALSE,Bacon Cheeseburger,,9,,FALSE,Chicken Curry,,9,,FALSE,Pea and Ham Soup,,4,,,,,
,FALSE,Pork Lo Mein,,7,,FALSE,Bacon Mushroom Burger,,10,,FALSE,Chicken Gumbo,,8,,FALSE,Pot Roast,,6,,,,,
,FALSE,Potato Cakes,,5,,TRUE,Bacon Sandwich,,5,,FALSE,Chili (Pam),,6,,FALSE,Potato and Leek Soup,,3,,,,,
,FALSE,Sausage in Bread,,16,,FALSE,BBQ Pulled Pork,,6,,FALSE,Coleslaw,,4,,FALSE,Potato Soup,,4,,,,,
,FALSE,Soft Pretzel,,5,,FALSE,Bean Burrito,,8,,FALSE,Creamed Corn,,4,,FALSE,Pumpkin Soup,,4,,,,,
,FALSE,Soft Pretzel and Mustard,,6,,FALSE,Beet Burger,,9,,FALSE,Curry Rice,,10,,FALSE,Rabbit Stew,,5,,,,,
,FALSE,Spaghetti,,7,,FALSE,BLT,,9,,FALSE,Eggplant Parm,,8,,FALSE,Raw Meaty Stew (Witchery),,1,,,,,
,FALSE,Spaghetti and Meatballs,,10,,FALSE,Cheese Sandwich,,4,,FALSE,Extreme Chili,,7,,FALSE,Rice Soup,,5,,,,,
,FALSE,Sunday Roast,,7,,FALSE,Cheeseburger (GT),,2,,FALSE,Fried Rice,,7,,FALSE,Seed Soup,,3,,,,,
,TRUE,Sweet Potato Souffle,,5,,FALSE,Cheeseburger (Pam),,8,,FALSE,General Tso's Chicken,,6,,FALSE,Spider Eye Soup,,3,,,,,
,FALSE,Toad in the Hole,,5,,FALSE,Chicken Sandwich,,7,,FALSE,Guacamole,,6,,TRUE,Split Pea Soup,,5,,,,,
,FALSE,Tuna Potato,,5,,FALSE,Coleslaw Burger,,6,,FALSE,Hash,,7,,FALSE,Suspicious Stew,,3,,,,,
,FALSE,Waffles,,5,,TRUE,Delighted Meal,,16,,TRUE,Herb Butter Parsnips,,4,,FALSE,Tomato Soup,,3,,,,,
,FALSE,Yorkshire Pudding,,3,,FALSE,Deluxe Cheeseburger,,10,,FALSE,Museli,,4,,FALSE,Turnip Soup,,5,,,,,
,FALSE,Zesty Zucchini,,9,,FALSE,Fish Sandwich,,7,,FALSE,Mushroom Risotto,,7,,FALSE,Ultimate Stew,,10,,,,,
,,,,,,FALSE,Fish Taco,,8,,FALSE,Nachoes,,5,,FALSE,Vegetable Soup,,6,,,,,
,,,,,,TRUE,Footlong,,9,,FALSE,Okra Creole,,4,,FALSE,Vishroom Stew,,3,,,,,
,,,,,,FALSE,Grilled Cheese,,7,,FALSE,Orange Chicken,,6,,,,,,,,,,
,,,,,,FALSE,Ham & Sweet Pickle Sandwich,,5,,FALSE,Oven Roasted Cauliflower,,5,,,,,,,,,,
,,,,,,FALSE,Hamburger (GT),,2,,FALSE,Paneer Tikka Masala,,6,,,,,,,,,,
,,,,,,FALSE,Hamburger (Pam),,7,,FALSE,Peas and Celery,,4,,,,,,,,,,
,,,,,,FALSE,Honey Sandwich,,4,,FALSE,Rainbow Curry,,13,,,,,,,,,,
,,,,,,FALSE,Hotdog,,6,,FALSE,Refried Beans,,4,,,,,,,,,,
,,,,,,TRUE,Large Bacon Sandwich,,10,,FALSE,Steamed Peas,,3,,,,,,,,,,
,,,,,,FALSE,Large Cheese Sandwich,,8,,FALSE,Veggie Stirfry,,8,,,,,,,,,,
,,,,,,FALSE,Large Steak Sandwich,,10,,FALSE,Vindaloo,,5,,,,,,,,,,
,,,,,,FALSE,Large Veggie Sandwich,,8,,TRUE,Zucchini Bake,,9,,,,,,,,,,
,,,,,,FALSE,Leafy Chicken Sandwich,,8,,,,,,,,,,,,,,,
,,,,,,FALSE,Leafy Fish Sandwich,,8,,,,,,,,,,,,,,,
,,,,,,FALSE,Onion Hamburger,,5,,,,,,,,,,,,,,,
,,,,,,FALSE,McPam,,8,,,,,,,,,,,,,,,
,,,,,,FALSE,Random Taco,,8,,,,,,,,,,,,,,,
,,,,,,FALSE,Steak Sandwich,,5,,,,,,,,,,,,,,,
,,,,,,FALSE,Taco,,8,,,,,,,,,,,,,,,
,,,,,,FALSE,Veggie Sandwich,,4,,,,,,,,,,,,,,,
,,,,,,FALSE,Veggieburger,,2,,,,,,,,,,,,,,,
"""

CSV_OTHER = """
,"GregTech New Horizons - Spice of Life Tracker, Other",,,,,,,,,,,,,
,0,Shanks Obtained (Out of 199),,,,,,,,,,,,
,,,,,,,,,,,,,,
,GregTech Processed Drinks,,,90,,GregTech Foods,,,18,,Unobtainable (Not Counted),,,2
,FALSE,Alcopops,,1,,FALSE,Chocolate Coin,,1,,,Terrawart,,1
,FALSE,Apple Juice (GT),,2,,FALSE,Chum,,3,,,Beetroot,,1
,FALSE,Beer,,3,,FALSE,Chum on a Stick,,3,,,,,
,FALSE,Cave Johnson's Grenade Juice,,1,,FALSE,Chumburger,,3,,,,,
,FALSE,Cherry Soda,,2,,FALSE,Fries (GT),,4,,,,,
,FALSE,Chilly Sauce,,1,,FALSE,Fries (In Foil),,4,,,,,
,FALSE,Chocolate Milk (GT),,2,,,,,,,,,,
,FALSE,Cider,,2,,Forestry,,,16,,,,,
,FALSE,Coffee (GT),,1,,FALSE,Ambrosia (Forestry),,4,,,,,
,FALSE,Cola Soda,,2,,FALSE,Curative Mead,,1,,,,,
,FALSE,Dark Beer,,2,,FALSE,Honey Pot,,1,,,,,
,FALSE,Dark Chocolate Milk,,2,,FALSE,Honeyed Slice,,4,,,,,
,FALSE,Diablo Sauce,,1,,FALSE,Mead,,5,,,,,
,FALSE,Diabolo Sauce,,1,,FALSE,Short Mead,,1,,,,,
,FALSE,Dragon Blood,,2,,,,,,,,,,
,FALSE,Energy Drink,,1,,Thaumcraft,,,67,,,,,
,FALSE,Ginger Ale,,2,,FALSE,Beef Nugget,,1,,,,,
,FALSE,Glen McKenner,,1,,FALSE,Chicken Nugget,,1,,,,,
,FALSE,Golden Apple Juice,,2,,FALSE,Chocolate Bar (TC),,1,,,,,
,FALSE,Golden Cider,,2,,FALSE,Chocolate Ice Cream (TC),,2,,,,,
,FALSE,Grape Juice (GT),,2,,FALSE,Dezil's Marshmallow,. . . . . .,50,,,,,
,FALSE,Grape Soda,,2,,FALSE,Fish Nugget,,1,,,,,
,FALSE,Grapefruit Soda,,2,,FALSE,Magic Funguar,,3,,,,,
,FALSE,Holy Water,,1,,FALSE,Mana Bean,,1,,,,,
,FALSE,Hops Juice,,1,,FALSE,Pork Nugget,,1,,,,,
,FALSE,Hot Sauce,,1,,FALSE,Taintberry,,1,,,,,
,FALSE,Ice Tea,,1,,FALSE,Tainted Fruit,,2,,,,,
,FALSE,Idun's Apple Juice,,2,,FALSE,Triple Meat Treat,,3,,,,,
,FALSE,Latte,,2,,,,,,,,,,
,FALSE,Lemon Juice,,1,,Blood Magic,,,1,,,,,
,FALSE,Lemon-Lime Soda,,3,,FALSE,Blood Orange,,1,,,,,
,FALSE,Lemonade (GT),,2,,,,,,,,,,
,FALSE,Leninade,,1,,Bees,,,1,,,,,
,FALSE,Limoncello,,1,,FALSE,Handful of Jelly Babies,,1,,,,,
,FALSE,Milk (GT),,1,,,,,,,,,,
,FALSE,Mineral Water,,1,,Biomes of Plenty,,,4,,,,,
,FALSE,Notches Brew,,2,,FALSE,Ambrosia (BoP),,3,,,,,
,FALSE,Orange Soda,,2,,FALSE,Filled Honeycomb,,1,,,,,
,FALSE,Pirate Brew,,2,,,,,,,,,,
,FALSE,Potato Juice,,2,,Tinker's Construct,,,2,,,,,
,FALSE,Purple Drink,,4,,FALSE,Bacon,,2,,,,,
,FALSE,Reed Water,,1,,,,,,,,,,
,FALSE,Root Beer,,2,,,,,,,,,,
,FALSE,Rum,,2,,,,,,,,,,
,FALSE,Scotch,,1,,,,,,,,,,
,FALSE,Strawberry Soda,,2,,,,,,,,,,
,FALSE,Sweet coffee,,1,,,,,,,,,,
,FALSE,Sweet Jesus Latte,,2,,,,,,,,,,
,FALSE,Sweet Latte,,2,,,,,,,,,,
,FALSE,Sweet Tea,,1,,,,,,,,,,
,FALSE,Tasty Clay,,1,,,,,,,,,,
,FALSE,Tea (GT),,1,,,,,,,,,,
,FALSE,Vinegar,,1,,,,,,,,,,
,FALSE,Vodka,,1,,,,,,,,,,
,FALSE,Wheaty Hops Juice,,1,,,,,,,,,,
,FALSE,Wheaty Juice,,1,,,,,,,,,,
,FALSE,Wine,,1,,,,,,,,,,
"""

CSV_FILES = {
    "T1 (Raw)": CSV_T1,
    "T2 (Basic)": CSV_T2,
    "T3 (Intermediate)": CSV_T3,
    "T4 (Advanced)": CSV_T4,
    "Other": CSV_OTHER
}

tier_db = {}
# Initialize the database logic once at startup
for tier_name, csv_content in CSV_FILES.items():
    tier_db[tier_name] = {"total_shanks": 0, "foods": {}}
    reader = csv.reader(io.StringIO(csv_content.strip()))
    for row in reader:
        # A food item always has TRUE/FALSE immediately preceding its name
        for j in range(len(row)):
            val = row[j].strip().upper()
            if val in ["TRUE", "FALSE"]:
                if j + 3 < len(row):
                    name = row[j+1].strip()
                    shanks_str = row[j+3].strip()
                    if name and shanks_str.isdigit():
                        shanks = int(shanks_str)
                        tier_db[tier_name]["foods"][name] = shanks
                        tier_db[tier_name]["total_shanks"] += shanks


def get_id_to_tag():
    """Reads level.dat to generate a mapping from numerical item IDs to String tags"""
    if not os.path.exists(LEVEL_DAT):
        print(f"Warning: {LEVEL_DAT} not found.")
        return {}
    
    id_to_tag = {}
    try:
        level = nbt.NBTFile(LEVEL_DAT, "rb")
        item_data = level["FML"]["ItemData"]
        for item in item_data:
            val = item["V"].value
            key = item["K"].value
            # Slice the first character (usually Forge's \x01 marker) as the Vue app did
            if isinstance(key, str) and len(key) > 0:
                tag = key[1:]
                id_to_tag[val] = tag
    except Exception as e:
        print(f"Error parsing level.dat: {e}")
    return id_to_tag

@app.get("/api/tiers")
def get_tiers():
    """Returns the parsed GTNH food categorizations"""
    return tier_db

@app.get("/api/players")
def get_players():
    """Enumerates uuid.dat files and fetches player info."""
    if not os.path.exists(PLAYERDATA_DIR):
        return {"players": []}
    
    players = []
    for f in os.listdir(PLAYERDATA_DIR):
        if f.endswith(".dat"):
            uuid = f[:-4]
            name = "Unknown"
            uuid_no_dashes = uuid.replace("-", "")
            
            # Fetch name from Mojang in the backend to avoid browser CORS errors
            try:
                resp = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid_no_dashes}", timeout=2)
                if resp.status_code == 200:
                    name = resp.json().get("name", "Unknown")
            except Exception:
                pass
            
            players.append({
                "uuid": uuid,
                "name": name,
                "face_url": f"https://api.mineatar.io/face/{uuid}?scale=12"
            })
    return {"players": players}

@app.get("/api/stats/all")
def get_combined_player_stats():
    players = get_players()["players"]
    playerCount = len(players)
    if(playerCount == 0):
        return {"error": "No players found"}
    returnData = {
            "playerCount": playerCount,
            "total_eaten": 0,
            "eaten": [],
            "categories": {},
            "percentages": {},
        }
    for player in players:
        playerStats = get_player_stats(player["uuid"])
        if "error" in playerStats:
            continue
        returnData["total_eaten"] += playerStats["total_eaten"]
        for food in playerStats["eaten"]:
            food_id = food["id"]
            food_tag = food["tag"]
            food_damage = food["damage"]
            food_hunger = food["hunger"]
            food_mod = food["mod"]
            #check if the food is already in the list
            found = False
            for f in returnData["eaten"]:
                if f["id"] == food_id and f["damage"] == food_damage:
                    f["count"] += 1
                    found = True
                    break
            if not found:
                returnData["eaten"].append({
                    "id": food_id,
                    "tag": food_tag,
                    "damage": food_damage,
                    "hunger": food_hunger,
                    "mod": food_mod,
                    "count": 1
                })
        for mod, count in playerStats["categories"].items():
            returnData["categories"][mod] = returnData["categories"].get(mod, 0) + count

    total_eaten = returnData["total_eaten"]
    percentages = {}
    for mod, count in returnData["categories"].items():
        percentages[mod] = round((count / total_eaten) * 100, 2) if total_eaten > 0 else 0
    returnData["percentages"] = percentages

    return returnData


@app.get("/api/stats/{uuid}")
def get_player_stats(uuid: str):
    """Generates and returns Spice of Life stats for a player."""
    uuid = os.path.basename(uuid)  # Sanitize input to prevent directory traversal

    file_path = os.path.join(PLAYERDATA_DIR, f"{uuid}.dat")
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "Player not found"})
    
    id_to_tag = get_id_to_tag()
    
    try:
        player_dat = nbt.NBTFile(file_path, "rb")
        foods_tag = player_dat["ForgeData"]["PlayerPersisted"]["SpiceOfLifeHistory"]["FullHistory"]["Foods"]
        
        eaten = []
        categories = {}
        
        for food in foods_tag:
            if "id" not in food:
                continue
            food_id = food["id"].value
            damage = food["Damage"].value if "Damage" in food else 0
            hunger = food["Hunger"].value if "Hunger" in food else 0
            
            tag = id_to_tag.get(food_id, str(food_id))
            mod = tag.split(":")[0] if ":" in tag else "unknown"
            
            eaten.append({
                "id": food_id,
                "tag": tag,
                "damage": damage,
                "hunger": hunger,
                "mod": mod
            })
            categories[mod] = categories.get(mod, 0) + 1
            
        total_eaten = len(eaten)
        percentages = {}
        for mod, count in categories.items():
            percentages[mod] = round((count / total_eaten) * 100, 2) if total_eaten > 0 else 0
            
        return {
            "uuid": uuid,
            "total_eaten": total_eaten,
            "eaten": eaten,
            "categories": categories,
            "percentages": percentages,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Mount the frontend directory
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)