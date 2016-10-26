PM: Project Management System
=======================================

PM is a project management sytem specifically designed to manage [tech transfer projects](https://en.wikipedia.org/wiki/Technology_transfer).


## Overview

### Project workflow

```
---------------------------------------------------------------------------------------------
#9  Pfizer        R&D  |xxxxx | Contract received by post          
#10 Sanofi        aR&D |xxxxx | Contract sent by post office       
#7  Novartis      R&D  |xxxxx | Elodie received the doc            
#6  J&J           R&D  |xxxx  | Get OK from university; still waiting answer from others
#8  BMS           R&D  |xxxx  | Recontact Thierry; still waiting for option proposal
#12 GSK           R&D  |x     | Wait for starting meeting 
---------------------------------------------------------------------------------------------           
```

Project workflow dashboard displays all the ongoing projects.
Information provided are:
* Id (used in the command to refer to the project);
* Short name;
* Status of the project which can be: `Start`, `Progr` (scientific program in discussion), `Budge` (budget in discussion), `Contr` (contract is being negociated), `Sign` (contract is in the signature process), `Done` (See command > commit for further details);
* Progress bar indicator until project completion;
* Date of last action;
* Useful comment on the last action.



### Project history

```
---------------------------------------------------------------------------------------------
Project #9  Pfizer     R&D   150 kEUR     Duration:  4 months
---------------------------------------------------------------------------------------------
   1   05/06/2016     --  Start |x     |  -                                  
   2   30/09/2016   117d  Sign  |xxxxx |  -                                  
   3   30/09/2016     0d  Sign  |xxxxx |  Wait for original by post office
---------------------------------------------------------------------------------------------    
```

Project history dashboard shows all the action made on the project.
Information provided are:
* Node of the action in the history (used in the command to refer to a particular action);
* Date of action;
* Number of days between the last action and the current one;
* Progress bar indicator;
* Comment on the action.



### Statistics

```
---------------------------------------------------------------
  Stats from 05/03/2015 to 30/09/2016      User: A.GAUTIER
---------------------------------------------------------------
  Total amount signed........  475 kEUR
     * Licenses..............    0 kEUR
     * R&D/MTA...............  475 kEUR
  Total amount in nego.......  857 kEUR
     * Licenses..............  120 kEUR
     * R&D/MTA...............  737 kEUR
---------------------------------------------------------------
  Cash per project...........   78 kEUR
  Cash per license...........   24 kEUR
  Cash per rnd...............  101 kEUR
---------------------------------------------------------------
  Number of projects
     * Total.................. 17
     * Signed................. 2
     * Active................. 15
  Number of licenses
     * Total.................. 5
     * Signed................. 0
     * Active................. 5
  Number of R&D
     * Total.................. 12
     * Signed................. 2
     * Active................. 10
---------------------------------------------------------------
  Average time to Done........  8 months
---------------------------------------------------------------
```


### Report

![Screenshot of report]
(https://github.com/theeko74/pm/blob/master/Example1.png)


## Install

It works with python3 on any platform (tested on Mac OS X and Windows).
To generate reports, you will need Word/Office.

1. Clone the repo;
2. Install dependencies via `requirements.txt`
3. Create a blank JSON file to be used as the database;
4. Run with python

```
git clone https://github.com/theeko74/pm
cd pm
pip install -r requirements.txt
mkdir database && cd database
touch db.json
python3 pm.py status
```

If you want to access anywhere the `pm` sytem, you will need to add it to the `PATH`:
* Unix
  * Open `.bash_profile` in your user directory;
  * Add `export PATH=/directory/to/pm/folder/:$PATH`;
  * Restart terminal.

* Windows
  * Settings > System > Advanced settings;
  * Environment variables > PATH > Add `/directory/to/pm/folder/`.
  * `chcp 65001` to display unicode characters in the cmd console.



## Settings

* `PROGRESS_CHR`, unicode character, styles the character for the loading bar.
* `PROGRESS`, dict, maps status of the project with loading bar indicator.
* `WIDTH`, int, defines the width of the table.
* `WARN_TIME`, int, defines the number of days before a red flag is shown.
* `DATABASE_FILE`, string, defines the filename for the databse in JSON format.



## Commands

* `pm status` displays the project workflow.
	* `pm status --all` or `-a` diplays all the projects (including the ones that are done);
	* `pm status -o [options]` sorts the project workflow table by options. Options take:
    * `date`
    * `status`
    * `name`

* `pm stats` displays the statistics on the current year. Options are:
	* `pm stats --start [-S] [DATE] --end [-E] [DATE]` displays the statistics between the start date and the ending date;
	* `pm stats --year [YEAR]` displays the statistics on the year.

* `pm history [ID]` displays the history of the project number [ID].

* `pm add -n "[PROJECT NAME]" -t "[PROJECT TYPE]" -m [EURO]` adds a new project to the workflow taken the mandatory parameters:
	* [PROJET NAME] name of the project;
	* [PROJECT TYPE] can be;
		* `R&D`;
		* `Lic` for license;
		* `aR&D` for amendment of a R&D;
		* `aLic` for amendment of a license;
	* [EURO] is potential amount in kEUR;

* `pm rm [ID]` removes the project [ID] from the workflow.

* `pm update [ID]` modify the project, with arguments:
  * `--name` changes the name of the project;
  * `--type` changes the type;
  * `--money` changes potential amount of the deal;
  * `--money-year` changes/adds the potential for the current year;
  * `--pi` changes/adds the name of the principal investigator;
  * `--summary` chnages/adds a summary of the project.


* `pm commit [ID]` commits a new action to the project number [ID]. Additionnal options can be added:
	* `--status [STATUS]` or `-s` changes the status of the project. It can be:
		* `Start` when the project just start (first meeting, etc.);
		* `Nego` when negociations are engaged with a partner;
		* `TS` when a termsheet is being discussed;
		* `Contr` when a contract is drafting;
		* `Sign` when the contract is in the signature process;
		* `Done` when the contract is signed and project closed.
	* `--message "[MESSAGE]"` or `-m` adds a message to the commit.
	* `--delete [NODE_NUMBER]` or `-d` deletes a node in the history of the project.

* `pm report` generates a word report saved in `./Report` folder. With argument `--excel` it generates a report in Excel.


## Database

Data are stored as JSON format to be easly exported to another app or webservice.

Example:
```javascript
{
    "projects": [
        {	
        	"id": 15,
            "money": 100,
            "money_year": 100,
            "name": "Sanofi",
            "type": "R&D",
            "summary": "Amazing project to deal with",
            "pi": "Eleine",
            "history": [
                {
                    "comment": "-",
                    "date": "2016-09-09T17:59:13.154581",
                    "node": 1,
                    "status": "Start"
                },
                {
                    "comment": "Wait for minutes of meeting validated",
                    "date": "2016-09-30T18:11:14.212896",
                    "node": 2,
                    "status": "Start"
                }
            ]
        }
	...
	]
}
```


