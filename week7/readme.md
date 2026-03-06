Overview and Purpose
    This is a backup planner that defines its settings in a json config file. this allows you to easily save or change, or even maintain multiple diffirent json files for diffirent uses. much easier than having to type in all of those settings as arguments when the script is run.
Usage Instructions
    run the script like this - python backup_planner.py backup_config.json 
    (or whatever your argument is)
Schema Design Decisions 
    Using a list makes it easier to parse multiple sources
    plan_name, sources, and destination are all required -version, description and options are all optional.
    include and exclude patterns is pretty much the file types you want backed up or not
Validation Levels
    1.load .json file to ensure it exists
    2.check that plan_name, sources, destination all exist
    3.verify they are the correct data types, strings, list, dict
    4.ensures that sources are not empty and that any included patterns are a list.
Simulation Logic
    i go by the outline you provided
Structure  
    load_config -> validate_config -> simulate_backup -> generate_report -> main()
    seperation of concerns is about making sure each function has one defined purpose
AI Usage
    I used the parts of code you provided with chatgpt to help get me a complete version with extra functionality.
Testing
    tested with the included backup_config and invalid_config