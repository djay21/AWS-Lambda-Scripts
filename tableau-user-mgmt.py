# Importing required libraries
import json
import tableauserverclient as TSC
import os
from datetime import datetime

# Defining disable/delete days
disable_days = 90
delete_days = 180

# Defining default user role on tableau
tableau_role = "Creator"

# Definong credentials
tableau_server_url = "http://172.16.2.200"
token_name = "lambda-function-auth"
token_value = "dew==:dew"

# Authenticating with tableau using PAT
tableau_auth = TSC.PersonalAccessTokenAuth(token_name, token_value, site_id='')
server = TSC.Server(tableau_server_url, use_server_version=True)
server.add_http_options({'verify': False})

# Get array of tableau user objects
def get_all_tableau_users():
    with server.auth.sign_in(tableau_auth):
        all_users, pagination_item = server.users.get()
    return all_users


# Create tableau user
def create_tableau_user(tableau_username, tableau_role):
    with server.auth.sign_in(tableau_auth):
        newUser = TSC.UserItem(name = tableau_username, site_role = tableau_role)
        newUser = server.users.add(newUser)

# Delete tableau user
def delete_tableau_user(tableau_user):
    with server.auth.sign_in(tableau_auth):
        server.users.remove(deleteUser.id)

# Make tableau user to unlicensed
def deactivate_tableau_user(tableau_user):
    with server.auth.sign_in(tableau_auth):
        tableau_user.site_role = "Unlicensed"
        server.users.update(tableau_user)

# Get array of inactive users
def get_inactive_users():
    user_details = get_all_tableau_users()
    inactive_users = []
    
    for user in user_details:
        if user.last_login != None and (datetime.today().date() - user.last_login.date()).days >= disable_days:
            inactive_users.append(user)        
    return inactive_users