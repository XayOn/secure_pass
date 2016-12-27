#!/usr/bin/env python
"""
Implement custom site methods for login, logout and pwchange

"""


class Facebook:
    """
    Facebook automation

    """
    def __init__(self, browser):
        self.browser = browser

    def login(self, user, pass_):
        """
        Login

        """
        self.browser.get("http://www.facebook.com")
        self.browser.find_element_by_id('email').send_keys(user)
        self.browser.find_element_by_id('pass').send_keys(pass_)
        self.browser.find_element_by_id('loginbutton').click()

    def logout(self):
        """
        Logout

        """
        self.browser.get("http://www.facebook.com")
        self.browser.find_element_by_id("show_me_how_logout_1").click()

    def change_password(self, old_key, new_key):
        """
        Change password

        """
        self.browser.get(
            "https://www.facebook.com/settings"
            "?tab=account&section=password&view")
        self.browser.find_element_by_id('password_old').send_keys(old_key)
        self.browser.find_element_by_id('password_new').send_keys(new_key)
        self.browser.find_element_by_id('password_confirm').send_keys(new_key)
