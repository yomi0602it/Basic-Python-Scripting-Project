

import os
import json
import shutil   #Allows for copy and overwrite operations

from subprocess import PIPE, run    #Allows for terminal commands
import sys  #Allows for command line arguments
#
GAME_DIR_PATTERN = "game"    #Specifies what name looking for in directory
GAME_CODE_EXTENSION = ".go"  #Specifies GO files
GAME_COMPILE_COMMAND = ["go", "build" ] #Compiles GO files 

def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

def find_all_game_paths(source):
    game_paths = []

    for root, dirs, files, in os.walk(source):  #only needs to be ran once
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)

        break
    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)

    return new_names

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def make_json_metadata(path, game_dirs):
    data = {        #Dictionary of game names
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)

def compile_game_code(path):    #Takes path to compile file inside of
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break
            
        break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("Compile result:", result)

    os.chdir(cwd)

def main(source, target):
    cwd = os.getcwd()   #Gets the directory file is run from
    source_path = os.path.join(cwd, source)    #Gets source path on any os
    target_path = os.path.join(cwd, target)     # Gets target directory path

    game_paths = find_all_game_paths(source_path)   #Found game paths
    new_game_dirs = get_name_from_paths(game_paths, "_game")    #New game directories
    
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs):    #Takes matching elements from two arrarys and combines into tupple
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata(json_path, new_game_dirs)

    

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass a source and target directory - only!")
    
    source, target = args[1:]
    main(source, target)
