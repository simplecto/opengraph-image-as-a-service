# Purpose
This utility generates opengraph images.

# How it works

## the short version
Make an HTTP request to the endpoint, pass it some parameters, and it will
return an image.

## The long version
This is a webserver process 

1. HTTP request received
1. Validate params
1. Generate an HTML page from a tempalte + parameters
1. Render that HTML page with a headless web browser
1. Screenshot the page using headless browser
1. Save that image out to a jpg
1. Return the image

# Using the service
Docker is probably the best way to kick the tires.

`docker run --name ogaas --rm -p 8000:8000 -v $PWD/templates:/templates ogaas`

That will get you going on port 8000

# Creating your own templates
Everything should live in your template file (css and HTML). See the examples 
to see how it can work for you.

