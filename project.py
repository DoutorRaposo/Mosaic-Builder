from mosaic import make_mosaic
import shutil
import sys
from keys.API_Keys import api_token
import requests
from os import makedirs, path
import urllib

headers = {"accept": "application/json", "Authorization": "Bearer " + api_token}


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--clear":
        while True:
            ans_mode = input(
                "You've entered clearing cache mode. Do you wish to remove all your downloaded files? This does not affect your photomosaics: (y/n): "
            )
            try:
                if ans_mode.lower() == "y":
                    shutil.rmtree("download/")
                    sys.exit("Download directory removed successfully.")
                elif ans_mode.lower() == "n":
                    sys.exit("Operation aborted.")
            except FileNotFoundError:
                sys.exit("Directory was not present.")

    if len(sys.argv) == 2 and sys.argv[1] == "--clearall":
        while True:
            ans_mode = input(
                "You've entered clearing ALL mode. Do you wish to remove all your downloaded files and photomosaics? (y/n): "
            )
            try:
                if ans_mode.lower() == "y":
                    shutil.rmtree("download/")
                    shutil.rmtree("photomosaics/")
                    sys.exit(
                        "Download and photomosaic directories removed successfully."
                    )
                elif ans_mode.lower() == "n":
                    sys.exit("Operation aborted.")
            except FileNotFoundError:
                sys.exit("Directories were not present.")

    while True:
        user_input = input("Type name of the artist: ")
        search_results = query_artists(user_input)
        if search_results["total_results"] > 0:
            break
    if search_results["total_results"] == 1:
        id = str(search_results["results"][0]["id"])
    if search_results["total_results"] > 1:
        print("Results: ")
        for index, result in enumerate(search_results["results"]):
            try:
                titles = [
                    x["title"] + " (" + x["release_date"].split("-")[0] + ")"
                    for x in result["known_for"]
                ]
                print(
                    f"{index + 1} - {result['name']}, known for {result['known_for_department'].lower()}, titles: {'; '.join([x for x in titles])}"
                )
            except KeyError:
                print(
                    f"{index + 1} - {result['name']}, known for {result['known_for_department'].lower()}."
                )

        while True:
            try:
                index_input = (
                    int(input("Please type the number of your preferred result: ")) - 1
                )
            except ValueError:
                continue
            if index_input < len(search_results["results"]) and index_input >= 0:
                break

        id = str(search_results["results"][index_input]["id"])

    details = get_details(id)
    path_name = "download/cache-" + id
    if not path.exists(path_name + "/cache.json"):
        path_image, path_dataset = exec_dl(details, path_name)
    else:
        while True:
            answer = input(
                "Looks like you maybe already downloaded this artist, do you wish to download again? (y/n): "
            )
            if answer.lower() == "y":
                path_image, path_dataset = exec_dl(details, path_name)
                break
            elif answer.lower() == "n":
                path_image = path_name + "/" + id + ".jpg"
                path_dataset = path_name + "/dataset/"
                break
    while True:
        min = 100
        max = 1000
        try:
            scale_percent = int(
                input(
                    f"How much you want to scale your final image? Default size is 100% (600x900px). Recommended scale is 500%. Please type an integer from {min} to {max}: "
                )
            )
        except ValueError:
            continue
        if min <= scale_percent <= max:
            break
    while True:
        min_tile = int(scale_percent * (3 / 100))
        max_tile = int(scale_percent * (10 / 100))
        try:
            tile_factor = int(
                input(
                    f"What you want the tile factor to be? For your inputed scale of {scale_percent}%, the recommended value is {int(scale_percent * (5/100))}. Please input an integer from {min_tile} to {max_tile}: "
                )
            )
        except ValueError:
            continue
        if min_tile <= tile_factor <= max_tile:
            break

    make_mosaic(path_image, path_dataset, details, tile_factor, scale_percent)
    while True:
        ans = input(
            "Do you wish to delete the cached files? Maintaining the files can help you try to generate again without having to download and check files. This option does not delete your current photomosaic (y/n): "
        )
        if ans.lower() == "y":
            shutil.rmtree(path_name)
            print("Directory removed successfully")
            break
        elif ans.lower() == "n" or ans.lower() == "":
            break


def exec_dl(details, path_name):
    if path.isdir(path_name):
        shutil.rmtree(path_name)
    filmography = get_filmography(details["movie_credits"])
    roles_list = list(filmography.keys())
    filtered_filmography = filter_filmography(filmography, roles_list)
    makedir(path_name)
    path_image = download_main_image(details, path_name)
    path_dataset = download_posters(filtered_filmography, path_name)
    return path_image, path_dataset


# Search for artist and returns a dict with all search results.
def query_artists(name):
    search_url = (
        "https://api.themoviedb.org/3/search/person?query="
        + name.replace(" ", "%20")
        + "&include_adult=false&language=en-US&page=1"
    )
    response = requests.get(search_url, headers=headers)

    return response.json()


# This function have the input of the ID of the subject and returns a relevant information, with the movie credits appended.
def get_details(id):
    details_url = (
        "https://api.themoviedb.org/3/person/"
        + id
        + "?append_to_response=movie_credits"
    )
    response = requests.get(details_url, headers=headers)
    return response.json()


# Gets all filmography of a subject and returns a dict that each key represents a job. This function takes a dict that is a result of the "details" function.
def get_filmography(filmography_json):
    filmography = {}
    for key in filmography_json:
        for movies in filmography_json[key]:
            try:
                if movies["job"] not in filmography:
                    filmography[movies["job"]] = []
                filmography[movies["job"]].append(movies)
            except KeyError:
                continue
    filmography["cast"] = filmography_json["cast"]
    list_roles = list(filmography.keys())
    ordered_list = sorted(list_roles, key=str.casefold)
    ordered_filmography = {k: filmography[k] for k in ordered_list}
    return ordered_filmography


# This function filters the filmography for the selected jobs and also changes the links of the posters so movies without posters can have a default image.
def filter_filmography(filmography, roles_list):
    filtered_filmography = {}
    for index in range(len(roles_list)):
        roles_list[index] = roles_list[index].lower()
    for role in filmography:
        if role.lower() in roles_list:
            filtered_filmography[role.lower()] = filmography[role]
    # This part is for adding a poster_path in case there is none.
    for key in filtered_filmography:
        for index, dkey in enumerate(filtered_filmography[key]):
            if dkey["poster_path"] == None:
                filtered_filmography[key][index][
                    "poster_path"
                ] = "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-38-picture-grey-c2ebdbb057f2a7614185931650f8cee23fa137b93812ccb132b9df511df1cfac.svg"
            else:
                filtered_filmography[key][index]["poster_path"] = (
                    "https://www.themoviedb.org/t/p/w600_and_h900_bestv2"
                    + filtered_filmography[key][index]["poster_path"]
                )
    return filtered_filmography


def download_posters(filmography, path_name):
    index = 0
    total_number = 0
    downloaded = 0
    for roles in filmography:
        for movies in filmography[roles]:
            total_number += 1
    for roles in filmography:
        for movies in filmography[roles]:
            if (
                movies["poster_path"]
                == "https://www.themoviedb.org/assets/2/v4/glyphicons/basic/glyphicons-basic-38-picture-grey-c2ebdbb057f2a7614185931650f8cee23fa137b93812ccb132b9df511df1cfac.svg"
            ):
                index += 1
                print(
                    f"Skipped: {movies['title']}, doesn't have a proper poster. File {index}/{total_number}"
                )
                continue
            movie_name = movies["title"].replace("/", "")
            movie_name = movie_name.replace(":", " -")
            movie_name = movie_name.replace("?", "")
            movie_name = movie_name.replace('"', "")
            filetype = movies["poster_path"].split(".")
            filename = path_name + "/dataset/" + movie_name + "." + filetype[-1]
            index += 1
            print(f"Downloading: {movie_name}. File {index}/{total_number}")
            urllib.request.urlretrieve(movies["poster_path"], filename)
            downloaded += 1
    print(f"{downloaded} files downloaded.")
    return path_name + "/dataset/"

# This function just downloads the main image for the mosaic
def download_main_image(details, path_name):
    path = (
        "https://www.themoviedb.org/t/p/w600_and_h900_bestv2" + details["profile_path"]
    )
    filetype = path.split(".")
    filename = path_name + "/" + str(details["id"]) + "." + filetype[-1]
    print(f"Downloading main image. Filename: {filename}")
    print(path)
    urllib.request.urlretrieve(path, filename)
    return filename

# This function makes a path for the dataset.
def makedir(path_name):
    if not path.isdir(path_name):
        makedirs(path_name)
        makedirs(path_name + "/dataset/")
        print(f"Directory made for {path_name}.")
    else:
        print("Directory already present.")


if __name__ == "__main__":
    main()
