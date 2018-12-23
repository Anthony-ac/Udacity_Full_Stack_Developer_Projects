# README for Udacity Items Catalog Project

The **main.py** file runs the **Weightlifting Application.**
The application is a program that does the following:

- Creates a website via working with its templates, css file and db.

- Creates JSON end points.

- reads, adds new, edits and deletes items from its database.

- Provides Google sign in and sign out.

- Allows users the ability to only be able to modify the items in the database when signed in.

## Installation

It is preferred if the gitbash terminal is used it can be downloaded [here](https://git-scm.com/downloads).

Install [virtual Box](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1).

Install [vagrant](https://www.vagrantup.com/downloads.html).

Download the [VM configuration](https://github.com/udacity/fullstack-nanodegree-vm.git) and place it in the Vagrant directory.

Extract the **Anthony_Cordova_Item_Catalog** folder to the **fullstack-nanodegree-vm\vagrant** directory. There should be a **Vagrantfile** in the directory.

In order to start up your virtual machine from gitbash: `cd` into your Vagrant\fullstack-nanodegree-vm\vagrant folder. Then input the following into your terminal (it may take a while as you attempt to bring your virtual machine up.):

```bash
vagrant up

vagrant ssh
```
Ensure all **.py** files, **client_secrets.JSON** file, **static** and **templates** directories are in the same location as the **Vagrantfile**.

Run the following in order:
	`python db_setup.py`
	`populate_db.py`
	`main.py`

Input **http://localhost:5000/** on to your preferred browser and begin to use the website.

## Contributing
Anthony Cordova and others welcome.

## References
[Udacity](https://www.udacity.com/)
[w3schools](https://www.w3schools.com/)