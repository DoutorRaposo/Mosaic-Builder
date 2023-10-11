from project import query_artists, get_details, get_filmography
import json


def test_query():
    with open("test/test_query.json", "r") as file:
        cache = json.load(file)
    assert cache == query_artists("Christopher Nolan")


def test_details():
    with open("test/test_details.json", "r") as file:
        cache = json.load(file)
    assert cache == get_details("525")


def test_filmography():
    with open("test/test_filmography_input.json", "r") as file:
        input = json.load(file)

    with open("test/test_filmography_output.json", "r") as file:
        output = json.load(file)

    assert output == get_filmography(input)
