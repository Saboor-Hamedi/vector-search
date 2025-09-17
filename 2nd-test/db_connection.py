import mysql.connector

import configparser
import os


def get_db_connection():
    config = configparser.ConfigParser()
    config.read(os.path.join("..", "db_config.ini"))
    try:
        return mysql.connector.connect(
            host=config["mysql"]["host"],
            user=config["mysql"]["user"],
            password=config["mysql"]["password"],
            database=config["mysql"]["database"],
            port=int(config["mysql"]["port"]),
            collation=config["mysql"]["collation"],
            charset=config["mysql"]["charset"],
        )
    except KeyError as e:
        print(f"Error: Missing configuration key in db_config.ini. Details: {e}")
        return None
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database. Details: {e}")
        return None
