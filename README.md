# Airpark Django Backend
Backend code for the airpark application. The server is hosted on heroku. So if you want to check the entire Airpark software together, just run the android application as you normally would and you don't need to run this code separately!

If you want to just checkout the REST api and the data they return, you can import the json collection into postman and start hitting the apis. 
Drive link: https://drive.google.com/drive/folders/1gyJntGlNC2Xe6eLBEvqYCw_Z7vS2fCSW?usp=sharing
Postman Software link : https://www.postman.com/

### To run it locally:
Take a clone of the code and navigate to the git root folder. Make sure python is installed on the system. Then from the terminal run the following command:

```
python airpark/manage.py runserver
```

This will run the server on your local machine. You can connect to it and hit apis. Example: http://127.0.0.1:8000/api/login-user but it will return an error since it requires some body paramaters. I again recommed using postman. Just import the collection above.

## Database
The database is hosted remotely on google cloud. You can access it using `MySQLWorkBench`. The credentials:
```
        'NAME': 'airpark_db',
        'USER': 'root',
        'PASSWORD': 'DM1iFjh6tEvAtrf7',
        'HOST': '34.89.83.124',
        'PORT': '3306',
```

Then you can run queries to access the data.
