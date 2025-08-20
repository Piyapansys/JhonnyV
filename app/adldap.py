import configparser
import time
import os
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, SUBTREE, AUTO_BIND_NO_TLS, AUTO_BIND_TLS_BEFORE_BIND,BASE,LEVEL,ALL_ATTRIBUTES
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, reqparse, fields

class ADAuthenticator:
    def __init__(self):
        self.ad_server = os.getenv('AD_SERVER')
        self.ad_domain = os.getenv('AD_DOMAIN')
        self.ad_user = os.getenv('AD_USERNAME')
        self.ad_password = os.getenv('AD_PASSWORD')
        
        self.formatted_user = f'{self.ad_user}@{self.ad_domain}'
        
        print(f"Attempting to connect to AD server: {self.ad_server}")
        print(f"With user: {self.formatted_user}")
        
        self.server = None
        self.connection = None
        self.connect_to_server()
 
    def connect_to_server(self):
        # Try different connection methods
        connection_methods = [
            (f'ldap://{self.ad_server}', AUTO_BIND_NO_TLS),
            (f'ldaps://{self.ad_server}', AUTO_BIND_TLS_BEFORE_BIND),
            (self.ad_server, AUTO_BIND_NO_TLS),
        ]
 
        for server_address, auto_bind in connection_methods:
            try:
                print(f"Attempting connection with: {server_address}")
                self.server = Server(server_address, get_info=ALL, connect_timeout=5)  # Set a connection timeout of 5 seconds
                self.connection = Connection(
                    self.server,
                    user=self.formatted_user,
                    password=self.ad_password,
                    authentication=SIMPLE,
                    auto_bind=auto_bind
                )
                print(f'Successfully connected to AD using {server_address}')
                return
            except Exception as e:
                print(f"Connection attempt failed: {str(e)}")
                time.sleep(2)  # Wait for 2 seconds before retrying
       
        raise Exception("All connection attempts failed. Please check your server address and network configuration.")
 
    # def get_all_users_by_person(self):
    #     if not self.connection.bound:
    #         print("Connection to AD server is not bound.")
    #         return None

    #     search_base = ','.join([f"DC={dc}" for dc in self.ad_domain.split('.')])
    #     search_filter = '(objectClass=person)'
    #     attributes = ['cn', 'mail', 'userPrincipalName', 'distinguishedName', 'sAMAccountName']

    #     print(f"Searching for all users with base: {search_base}")
    #     print(f"Search filter: {search_filter}")

    #     if not self.connection.search(search_base=search_base, search_filter=search_filter, search_scope=SUBTREE, attributes=attributes):
    #         print(f"Search failed: {self.connection.result}")
    #         return None

    #     users = []
    #     for entry in self.connection.entries:
    #         user = {
    #             'name': entry.cn.value if hasattr(entry, 'cn') else "No Name",
    #             'email': entry.mail.value if hasattr(entry, 'mail') else None,
    #             'userPrincipalName': entry.userPrincipalName.value if hasattr(entry, 'userPrincipalName') else None,
    #             'distinguishedName': entry.distinguishedName.value if hasattr(entry, 'distinguishedName') else None
    #         }
    #         users.append(user)

    #     print(f"Found {len(users)} users")
    #     return users

    def get_all_users_by_person(self):
        if not self.connection.bound:
            print("Connection to AD server is not bound.")
            return None

        search_base = ','.join([f"DC={dc}" for dc in self.ad_domain.split('.')])
        search_filter = '(objectClass=person)'
        attributes = ['cn', 'mail', 'userPrincipalName', 'distinguishedName', 'sAMAccountName']

        print(f"Searching for all users with base: {search_base}")
        print(f"Search filter: {search_filter}")

        users = []
        # Enable paged search
        self.connection.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=attributes,
            paged_size=1000
        )

        while True:
            for entry in self.connection.entries:
                user = {
                    'name': entry.cn.value if hasattr(entry, 'cn') else "No Name",
                    'email': entry.mail.value if hasattr(entry, 'mail') else None,
                    'userPrincipalName': entry.userPrincipalName.value if hasattr(entry, 'userPrincipalName') else None,
                    'distinguishedName': entry.distinguishedName.value if hasattr(entry, 'distinguishedName') else None
                }
                users.append(user)

            # Check if there's a next page
            cookie = self.connection.result['controls'].get('1.2.840.113556.1.4.319', {}).get('value', {}).get('cookie')
            if cookie:
                self.connection.search(
                    search_base=search_base,
                    search_filter=search_filter,
                    search_scope=SUBTREE,
                    attributes=attributes,
                    paged_size=1000,
                    paged_cookie=cookie
                )
            else:
                break

        print(f"Found {len(users)} users")
        return users

    def authenticate(self, username, password):
        all_users = self.get_all_users_by_person()
    
        # # ตรวจสอบว่า username ไม่มีใน all_users
        # if not any(each.get('email') == username for each in all_users):
        #     all_users = self.get_all_users_by_engineer()

        if not all_users:
            print("Failed to retrieve users from AD")
            return False

        if username is None:
            print("Username is None")
            return False

        # Try to find the user by email, userPrincipalName, or sAMAccountName
        user = next((u for u in all_users if 
                    (u.get('email') and u['email'].lower() == username.lower()) or 
                    (u.get('userPrincipalName') and u['userPrincipalName'].lower() == username.lower()) or 
                    (u.get('sAMAccountName') and u['sAMAccountName'].lower() == username.lower())), None)
        
        if not user:
            print(f"User with identifier {username} not found")
            return False

        user_dn = user.get('distinguishedName')
        if not user_dn:
            print(f"User found, but distinguishedName is missing")
            return False

        print(f"Found user DN: {user_dn}")
        print(f"User attributes: {user}")  # Add this line to print all user attributes

        auth_methods = []
        if user.get('sAMAccountName'):
            auth_methods.append(('NTLM', NTLM, f'{self.ad_domain}\\{user["sAMAccountName"]}'))
        auth_methods.append(('SIMPLE', SIMPLE, user_dn))

        for auth_name, auth_method, auth_user in auth_methods:
            try:
                print(f"Attempting to authenticate with {auth_name} user: {auth_user}")
                user_conn = Connection(self.server, user=auth_user, password=password, authentication=auth_method)
                if user_conn.bind():
                    print(f'User authentication successful using {auth_name}')
                    user_details = self.parse_dn(user_dn)
                    user_details.update({
                        'name': user.get('name', ''),
                        'email': user.get('email', ''),
                        'userPrincipalName': user.get('userPrincipalName', ''),
                        'sAMAccountName': user.get('sAMAccountName', '')
                    })
                    print(f"User details: {user_details}")
                    return user_details
                else:
                    print(f"Failed to authenticate user with {auth_name}: {user_conn.result}")
                    print(f"Extended error information:")
                    print(f"  Result: {user_conn.result['result']}")
                    print(f"  Description: {user_conn.result['description']}")
                    print(f"  Message: {user_conn.result['message']}")
                    print(f"  Diagnostic Message: {user_conn.result.get('diagnosticMessage', 'N/A')}")
            except Exception as e:
                print(f"Authentication error with {auth_name}: {str(e)}")

        print("All authentication methods failed")
        return False

    def parse_dn(self, dn):
        dn_parts = dn.split(',')
        dn_dict = {}
        key_list = ['CN', 'OU1', 'OU2', 'OU3', 'DC1', 'DC2']
        ou_count = 0
        dc_count = 0

        for part in dn_parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip().upper()
                value = value.strip()

                if key == 'CN':
                    dn_dict['CN'] = value
                elif key == 'OU':
                    ou_count += 1
                    if ou_count <= 3:
                        dn_dict[f'OU{ou_count}'] = value
                elif key == 'DC':
                    dc_count += 1
                    if dc_count <= 2:
                        dn_dict[f'DC{dc_count}'] = value

        # Ensure all keys are present, even if empty
        for key in key_list:
            if key not in dn_dict:
                dn_dict[key] = ''

        return dn_dict




# import os
# import time
# from ldap3 import Server, Connection, ALL, SIMPLE, SUBTREE, Tls
# import ssl


# class ADAuthenticator:
#     def __init__(self):
#         self.ad_server = os.getenv('AD_SERVER')
#         self.ad_domain = os.getenv('AD_DOMAIN')
#         self.ad_username = os.getenv('AD_USERNAME')
#         self.ad_password = os.getenv('AD_PASSWORD')

#         self.formatted_user = f'{self.ad_username}@{self.ad_domain}'
#         self.server = None
#         self.connection = None

#         print(f"Attempting to connect to AD server: {self.ad_server}")
#         print(f"With user: {self.formatted_user}")

#         self.connect_to_server()

#     def connect_to_server(self):
#         try:
#             tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)

#             self.server = Server(self.ad_server, use_ssl=True, get_info=ALL, tls=tls_config, connect_timeout=5)
#             self.connection = Connection(
#                 self.server,
#                 user=self.formatted_user,
#                 password=self.ad_password,
#                 authentication=SIMPLE,
#                 auto_bind=True
#             )

#             print("✅ Successfully connected to AD via LDAPS (port 636)")

#         except Exception as e:
#             print(f"❌ LDAP connection failed: {e}")
#             raise Exception("All connection attempts failed. Please check your server address, network, or credentials.")

#     def get_all_users_by_filter(self, search_filter):
#         if not self.connection.bound:
#             print("Connection to AD server is not bound.")
#             return None

#         search_base = ','.join([f"DC={dc}" for dc in self.ad_domain.split('.')])
#         attributes = ['cn', 'mail', 'userPrincipalName', 'distinguishedName', 'sAMAccountName']

#         print(f"Searching AD with base: {search_base}, filter: {search_filter}")
#         success = self.connection.search(
#             search_base=search_base,
#             search_filter=search_filter,
#             search_scope=SUBTREE,
#             attributes=attributes
#         )

#         if not success:
#             print(f"Search failed: {self.connection.result}")
#             return None

#         users = []
#         for entry in self.connection.entries:
#             user = {
#                 'name': entry.cn.value if hasattr(entry, 'cn') else "No Name",
#                 'email': entry.mail.value if hasattr(entry, 'mail') else None,
#                 'userPrincipalName': entry.userPrincipalName.value if hasattr(entry, 'userPrincipalName') else None,
#                 'distinguishedName': entry.distinguishedName.value if hasattr(entry, 'distinguishedName') else None,
#                 'sAMAccountName': entry.sAMAccountName.value if hasattr(entry, 'sAMAccountName') else None,
#             }
#             users.append(user)

#         print(f"Found {len(users)} users")
#         return users

#     def get_all_users_by_person(self):
#         return self.get_all_users_by_filter('(objectClass=person)')

#     def get_all_users_by_engineer(self):
#         return self.get_all_users_by_filter('(description=Engineer)')

#     def authenticate(self, username, password):
#         all_users = self.get_all_users_by_person()

#         if not any(u.get('email') == username for u in all_users):
#             all_users = self.get_all_users_by_engineer()

#         if not all_users or username is None:
#             print("Failed to find matching users or username is None")
#             return False

#         user = next((u for u in all_users if
#                     (u.get('email') and u['email'].lower() == username.lower()) or
#                     (u.get('userPrincipalName') and u['userPrincipalName'].lower() == username.lower()) or
#                     (u.get('sAMAccountName') and u['sAMAccountName'].lower() == username.lower())), None)

#         if not user or not user.get('distinguishedName'):
#             print(f"User not found or missing DN for {username}")
#             return False

#         user_dn = user['distinguishedName']
#         print(f"Found DN: {user_dn}")

#         try:
#             user_conn = Connection(
#                 self.server,
#                 user=user_dn,
#                 password=password,
#                 authentication=SIMPLE,
#                 auto_bind=True
#             )

#             if user_conn.bound:
#                 print("✅ Authentication successful")
#                 user_details = self.parse_dn(user_dn)
#                 user_details.update({
#                     'name': user.get('name', ''),
#                     'email': user.get('email', ''),
#                     'userPrincipalName': user.get('userPrincipalName', ''),
#                     'sAMAccountName': user.get('sAMAccountName', '')
#                 })
#                 return user_details
#             else:
#                 print(f"❌ Authentication failed: {user_conn.result}")
#         except Exception as e:
#             print(f"❌ Error during authentication: {str(e)}")

#         return False

#     def parse_dn(self, dn):
#         dn_parts = dn.split(',')
#         dn_dict = {}
#         key_list = ['CN', 'OU1', 'OU2', 'OU3', 'DC1', 'DC2']
#         ou_count = 0
#         dc_count = 0

#         for part in dn_parts:
#             if '=' in part:
#                 key, value = part.split('=', 1)
#                 key = key.strip().upper()
#                 value = value.strip()

#                 if key == 'CN':
#                     dn_dict['CN'] = value
#                 elif key == 'OU':
#                     ou_count += 1
#                     if ou_count <= 3:
#                         dn_dict[f'OU{ou_count}'] = value
#                 elif key == 'DC':
#                     dc_count += 1
#                     if dc_count <= 2:
#                         dn_dict[f'DC{dc_count}'] = value

#         for key in key_list:
#             if key not in dn_dict:
#                 dn_dict[key] = ''

#         return dn_dict
