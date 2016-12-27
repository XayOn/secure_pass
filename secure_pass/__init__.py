"""
KeyStore

Usage:
    keystore --path <PATH> --recipient <RECIPIENT> --list-sites
    keystore --path <PATH> --recipient <RECIPIENT> --get --site_name <NAME> \
--username <USERNAME>
    keystore --path <PATH> --recipient <RECIPIENT> --delete \
--site_name <NAME>

Options:
    --path=<path>           Path to keystore
    --recipient=<recipient> GPG recipient to encrypt against
    --list-sites            list-sites
    --get
    --delete
    --site_name=<name>      Site name
    --username=<username>   Username for that site

Examples:
    keystore --path ".passwords" --recipient "me@davidfrancos.net" --list-sites

"""

# pylint: disable=import-error, too-few-public-methods

import glob
import os
import logging
from contextlib import suppress
from functools import lru_cache
from selenium import webdriver
import shutil
from getpass import getpass
import gnupg
import git
from docopt import docopt
import pyperclip
from . import automation

logging.basicConfig()
LOG = logging.getLogger(__name__)
GPG = gnupg.GPG(gnupghome=os.path.expanduser('~/.gnupg'))


class Key:
    """
    Represents a GPG Encrypted key

    """
    def __init__(self, file_, recipient, repo=False):
        self.file_ = file_
        self.recipient = recipient
        self.repo = repo

    @property
    def key(self):
        """
        Return decrypted key

        """
        return GPG.decrypt_file(
            open(self.file_, 'rb'), passphrase=getpass()).data

    @key.setter
    def key(self, key):
        """
        Encrypts a key and saves it in the keystore

        """
        with open(self.file_, 'wb') as file_:
            file_.write(GPG.encrypt(key, self.recipient).data)

        if isinstance(self.repo, git.Repo):
            # pylint: disable=no-member
            self.repo.index.add([os.path.abspath(self.file_)])
            self.repo.index.commit("Updated key")
            LOG.debug("Commited new key")

    def to_clipboard(self):
        """
        Save a key to clipboard

        """
        pyperclip.copy(self.key.decode('utf-8'))

    def __repr__(self):
        return str(self.file_)


class Site:
    """
    Represents a site.
    It reads from a directory structure like:
    - Site
      - [config.json]
      - {username}.asc
      - {username}.asc
      - ...

    """
    repo = False
    site_type = False

    def __init__(self, path, recipient, site_type):
        def get_name(name):
            """
            Given a key name, return username

            """
            return os.path.basename(name).replace('.asc', '')

        self.site_type = site_type

        with suppress(git.InvalidGitRepositoryError):
            self.repo = git.Repo(os.path.join(path, '..'))

        self.keys = {get_name(key_path): Key(key_path, recipient, self.repo)
                     for key_path in glob.glob("{}/*.asc".format(path))}

    def __repr__(self):
        return str(self.keys)

    def get(self, username):
        """ Return a key for a given username """
        return self.keys[username].key

    @property
    def browser(self):
        """
        Browser if type available

        """
        if self.site_type:
            return webdriver.Chrome()

    @property
    def automation(self):
        """
        Automation

        """
        return getattr(automation, self.site_type)(self.browser)

    def login(self, username):
        """
        Use selenium to login into site

        .. TODO: Handle sessions with selenium and isolate logins
                 in different windows

        """
        if not self.browser:
            assert RuntimeError("Cant use browser methods "
                                "without a config for this site")
        return self.automation.login(username, self.keys[username].key)

    def logout(self):
        """
        Use selenium to logout site

        """
        if not self.browser:
            assert RuntimeError("Cant use browser methods "
                                "without a config for this site")
        self.automation.logout()

    def change_password(self, username, newkey):
        """
        Use selenium to change password

        """
        if not self.browser:
            assert RuntimeError("Cant use browser methods "
                                "without a config for this site")

        return self.automation.change_password(
            username, self.keys[username].key, newkey)


class KeyStore:
    """
    Represents a complete keystore.
    - GPG encrypted files for each site in a directory
    - Directory-tree based sites tree

    """

    def __init__(self, dir_, recipient):
        self.dir_ = os.path.abspath(dir_)
        self.key = recipient

    @lru_cache()
    def _tree(self):
        """
        Populate keystore tree

        """
        for dir_ in os.listdir(self.dir_):
            if dir_ == ".git":
                continue
            yield (dir_.replace('/', ''),
                   Site(os.path.join(self.dir_, dir_), self.key, False))

    @property
    @lru_cache()
    def sites(self):
        """
        Keystore tree dict

        """
        return dict(self._tree())

    def list_sites(self):
        """ Print sites """
        print(self.sites)

    def add_site(self, name, username, pass_):
        """
        Add a site, empty, with only pass
        and default configuration

        """
        path = os.path.join(self.dir_, name)
        os.makedirs(path)
        site = Site(path, username, self.key)
        site.keys[username].key = pass_

    def delete(self, name):
        """
        Delete a site

        """
        shutil.rmtree(os.path.join(self.dir_, name))


def main():
    """
    CLI

    """

    def clean(what):
        """ Clean an argument from docopt """
        return what.replace("--", "").replace("-", "_")

    def get_action(args):
        """
        Given a args dict, return action

        """
        actions = ["--get", "--delete", "--list-sites"]
        action = [a for a in actions if args[a]][0]
        args.pop(action)
        return clean(action)

    args = docopt(__doc__)
    dest = KeyStore(args.pop("--path"), args.pop("--recipient"))
    if args["--site_name"]:
        dest = dest.sites[args.pop('--site_name')]
    action = get_action(args)
    return getattr(dest, action)(**{clean(a): b for a, b in args.items() if b})


if __name__ == "__main__":
    main()
