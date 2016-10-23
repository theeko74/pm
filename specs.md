PM: Project Management
=======================================

PM is a project management sytem used specifically to manage [tech transfer projects](https://en.wikipedia.org/wiki/Technology_transfer).

## Commands

* `pm status` display the workflow.
* `pm add -n "Fluidigm" -t "R&D" -m 100` add a project Fluidigm type R&D for 100k€.
* `pm action 001 "First meeting"` add action "first meeting" in project #001.
* `pm history 001` lists all actions of the project 001.
* `pm stats` display stats on the workflow.
* `pm stats [project-id]` display stats on the project.
* `pm report` make a report in PDF or word file.

#### Status

`pm status` display the workflow. It lists all the projects currently ongoing with information such: name of the project, type of agreement, status, date of last action, comment.

Example: 
```
PM Status
----------------------------------------------------------------------------------------------
#001 Sanofi 	R&D 		Nego. 	XX    	12/05/2016 	Wait for add information from Jane
														and other people
#010 Torca	 	License 	Nego. 	XX    	09/09/2016 	Wait for Alex return
#005 Pfizer 	R&D 		Start 	X     	25/09/2016 	Need to prepare the draft
``` 
Sort by date of last action, ascending.

Status can be:
* X Start: begining of the project, first meeting, etc.
* XX Nego: work on the R&D plan and the budget, have presentation with potential partners.
* XXX TS: work on a termsheet
* XXXX Contract: draft of the contract, negociations, final version.
* XXXXX Sign: contract in the signature process.
* XXXXXX Done: project is finished and closed.


#### Add project

`pm add -n "[Name]" -t "[Type of contract]" -m [Number]` add a project in the workflow with parameters n as name of the project, -t type of contract (R&D, license, Am. R&D, etc.), -m the potential amount in euros.
Ex: `pm add -n "Fluidigm" -t "R&D" -m 100`


#### Add action

`pm action [project-id] "Comment"` add a new action to the project #1 and the comment.


#### Show history

`pm history [project-id]` list history of a project

Example: 
```
Projet #001: Fluidigm R&D
----------------------------------------------------------------------
d3f45e	Start 		12/05/2016	 -
d4f65e	Start 		12/05/2016	 First meeting
f5r4e5	Nego 		22/05/2016	 First R&D project written
d3f45e	TS			10/06/2016	 TS is ready to be sent
f5r4e5	Contract	09/09/2016	 Draft of the contract to be sent
d3f45e	Sign		12/09/2016	 In the signature proccess
f5r4e5	Done		22/09/2016	 -
```


## Database

Data will be stored as JSON format (for future exporting) in a file.

Format:
```javascript
{
	"projects": [
		{
			"id": 1,
			"name": "Pfizer",
			"type": "R&D",
			"money": 100,
			"history":[
				{
					"node": 1,
					"status": "Start",
					"date": "2016-04-23T18:35:50.511Z",
					"comment": "-"
				},
				{
					"node": 2,
					"status": "Start",
					"date": "2016-04-23T18:35:50.511Z",
					"comment": "First meeting"
				},
				{
					"node": 3,
					"status": "Nego",
					"date": "2016-04-23T18:35:50.511Z",
					"comment": "First R&D project written"
				}
			]
		}
	]
}
```


## Code

* Written in Python@3.4
* Objects:
  * `Workflow` with methods: add_project, status, stats, report
  * `Project` with methods: add_action, stats, show_history