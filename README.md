# Mosaic Builder
#### Video Demo:  https://youtu.be/nMIECGcPBSU
#### Description:
My final project is Mosaic Builder: a python script that creates a mosaic of a portrait using the image of all the posters of a artist of your choice.

You can search for an artist, there will a way to choose which one you like if there's more than one result. The script will then download all the posters and give you options to build your mosaic.

### Features:
- You can clear all the downloaded files but the finished mosaics in the end of the process or by using the --clear command line argument
- You can clear everything including the finished mosaic by using the --clearall command line argument
- You can adjust the scaling of the finished image, as well as the tile size for each image.
- If you like to try to mess around with the settings, you can skip the downloading part. The scripts detects and asks you if you want to download again (maybe if the internet dropped, you could redownload!). Otherwise, it will use the content that is already in the folder.
- There are recommended values for optimal mosaics, but you can mess around and find out! The recommended scale is too big for codespaces, but you can download or try the default scale.

### File structure:

This project uses some of the code that I used for protoyping my CS50X final project and also a mosaic builder that I created for myself while studying CS50P. There is a helper file that is the mosaic builder, functioning as a library. The remaining functions are inside de project.py file. There is also a bunch of testing mock JSON that I used for testing a few of the functions.

The artist's info is all TMDB's API.

When you download the contents of an artist, the script will create a folder with the ID of the artist, download the dataset for the mosaic in a folder, a portrait of the artist and when the mosaic script runs, a JSON file with all the average colors of the dataset is also created.

This enables the user to reuse the program and just mess with the scaling if he wants to.

### ABOUT MYSELF AND THE PROCESS:
My name is Rafael de Andrade. I'm from Curitiba, Brazil.

I'm a photographer and I got a little curious about image editing through Python and we learn the basics of doing it with C in CS50x. Thought this was a great way to combine both of these knowledges!

My project for CS50x was originally creating a mosaic, but I basically used the API knowledge to create a web app, because I was more prepared to do this with the knowledge of X. I revisited the concept for CS50P and was able to finish the idea.