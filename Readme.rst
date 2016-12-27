Secure Pass
-----------

This is a more pythonic implementation of ``pass``
(https://www.passwordstore.org/).

I liked ``pass`` main features:

- File-based password tree
- Git-based (optional)
- GPG encryption (individual files, only one password will
  be decrypted at a time)


Yet I missed a few things:

- Automatic password changing
- Auto-login

I also didn't want to make it a firefox/chrome extensions, as
that can be compromised and it's not flexible enough.
That part made me thing about using selenium for that matter,
wich then lead to:

- Individually isolated sessions (TODO)
- Multiple browser support (every one that selenium has support for)

So I wrote ``secure_pass``. This is still a work in progress and needs
quite a lot polishing (and documentation).