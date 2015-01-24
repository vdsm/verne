Verne
=====

Towards a social operating system.

Install
-------

    virtualenv .env
    . .env/bin/activate
    bash install_pygit2.sh
    pip install -r requirements.txt

(maybe)

Layout
------

The folder structure is designed to look like a filesystem root, ie, / in a Unix environment.

It is a single user operating system which can incorporate data and code from other users automatically.

`/bin` contains a set of software tools chosen by the user for their day to day activities.

`/var` is the termination point for repositories which are shared across the network.
