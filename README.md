# Style transfer playground web app

See the inner workings of the style transfer algorithm presented in [A Neural Algorithm of Artistic Style](https://arxiv.org/pdf/1508.06576v2.pdf) in real time from the comfort of your web browser with this application built on Flask and Tensorflow. Think of it like the popular Prisma app except with much greater user customization and it allows you an inside look at the intermediate part of the image generation process.

After logging in through one of our supported OAuth providers, you and your users can create custom images blending your own style and content images. After uploading your images and clicking "Create image" on the "Create an image" tab, the server kicks off a Tensorflow implementation of the style transfer algorithm. The resulting page that the user sees is streamed using Flask's content streaming so that the generated image gets updated on each iteration in real time.

Upon completion of the computation, you can see a gif of the entire process of your image's creation (made with the [Gifshot](https://github.com/yahoo/gifshot) Javascript library). If desired, save your generated images to your user profile for later viewing and to share with friends, which creates a database entry for your image and saves it to the local filesystem. We use a sqllite database with SQLAlchemy.

## Prerequisites

This app was written for Python 3, and its compatibility with Python 2 has not been tested.

All package dependencies are listed in `requirements.txt`. Note that the Tensorflow URL is for the Linux version: for other versions replace it with the corresponding URL from the [Tensorflow setup guide](https://www.tensorflow.org/versions/r0.11/get_started/os_setup.html). Otherwise, the appropriate dependencies can be installed with
```
pip install -r requirements.txt
```

You will also need to download the file `imagenet-vgg-verydeep-19.mat` found [here](http://www.vlfeat.org/matconvnet/pretrained/) into the top level of the project directory. This file contains the pretrained 19-layer VGG convolutional neural network, which is used by the style transfer algorithm.

Finally, before running the app for the first time, you must create the sqllite database by running the `db_create.py` script.

## Running
To start the Flask server on the default port 5000, run the script `run.py` from your Python console. You will also need to run a second simple server on port 8000 from the top level of the project directory, which is responsible for serving the images and gifs while the large Tensorflow computation is running. Any simple server with CORS enabled will work: I suggest Node's `http-server`:
```
npm install http-server -g
http-server -p 8000 --cors
```

Then simply visit `http://localhost:5000/` in your web browser.

## Migrations and testing
If you choose to modify the app source code, you may wish to know how we do migrations and unit testing.

If you modify any of the models in `models.py`, you need to run the script `db_migrate.py` to see the changes reflected in the SQL database. (Note: the scripts `db_create.py` and `db_migrate.py` were borrowed from Miguel Grinberg's [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).)

Unit tests were implemented with python's Unittest framework and can be run with the script `tests.py`. Modify these tests according to any new features you might add or tweak. We also use the `coverage` module to report test coverage: html versions of the coverage report can be found in `tests/coverage` once the test suite has been run.

## Examples
Here are some screenshots demonstrating the Style Transfer Playground in use:

Pre-login:
![Pre-login]
(https://github.com/aheyman11/style-transfer-playground/blob/master/screenshots/login.png)

Image upload:
![Image upload]
(https://github.com/aheyman11/style-transfer-playground/blob/master/screenshots/upload.png)

Mid-image creation:
![Mid-image creation]
(https://github.com/aheyman11/style-transfer-playground/blob/master/screenshots/mid-computation.png)

Post-image creation:
![Post-image creation]
(https://github.com/aheyman11/style-transfer-playground/blob/master/screenshots/post-computation.png)

User profile:
![User profile]
(https://github.com/aheyman11/style-transfer-playground/blob/master/screenshots/profile.png)
