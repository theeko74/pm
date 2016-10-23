#!/usr/bin/env python3
"""
Runtime module to handle the command and interact with the pmlib.
"""

import argparse, os, datetime

import lib.pmlib as pmlib
import lib.export as export
import settings



def main():

	# Parser options
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(help='all commands to interact with pm', dest='command')

	# Subparser status
	status_parser = subparsers.add_parser('status', help="display status of the workflow")
	status_parser.add_argument('-l', '--all', action='store_true', default=False,
							   help="display ongoing and done projects")
	status_parser.add_argument('-o', '--sort', action='store', dest='sort_key', default='status',
							   help="sort project by key")

	# Subparser stats
	stats_parser = subparsers.add_parser('stats', help="display statistics")
	stats_parser.add_argument('-S', '--start', action='store', dest='start_date', default=None, 
							  help='specify a starting date to calculate the statistics')
	stats_parser.add_argument('-E', '--end', action='store', dest='end_date', default=None,
							  help='specify an ending date to calculate the statistics')
	stats_parser.add_argument('-Y', '--year', action='store', dest='year', default=None,
							  help='stats for the indicated year: starting at 1/01, end 31/12')
	stats_parser.add_argument('--all-year', action='store_true', default=False,
							  help='stats for all years in database')
	
	# Subparser history
	history_parser = subparsers.add_parser('history', help="display the history of a project")
	history_parser.add_argument('id', type=int)

	# Subparser add project
	add_parser = subparsers.add_parser('add', help="add a new project in the workflow")
	add_parser.add_argument('name', type=str)
	add_parser.add_argument('type', type=str)
	add_parser.add_argument('money', type=int)

	# Subparser update project
	update_parser = subparsers.add_parser('update', help="add new information to the project")
	update_parser.add_argument('id', type=int)
	update_parser.add_argument('--money-year', type=int)
	update_parser.add_argument('--summary', type=str)
	update_parser.add_argument('--pi', type=str)
	update_parser.add_argument('--name', type=str)
	update_parser.add_argument('--type', type=str)
	update_parser.add_argument('--money', type=int)
	update_parser.add_argument('--ref', type=str)

	# Subparser del project
	del_parser = subparsers.add_parser('rm', help="remove a project of the workflow")
	del_parser.add_argument('id', type=int)

	# Subparser commit
	commit_parser = subparsers.add_parser('commit', help="commit a new action to a project")
	commit_parser.add_argument('id', type=int)
	commit_parser.add_argument('-s', '--status', action='store', dest='status', default="",
							   help="change the status of the project during the commit")
	commit_parser.add_argument('-m', '--message', action='store',  dest='commit', default="-",
							   help="add a comment to the commit")
	commit_parser.add_argument('-d', '--delete', action='store', default=None, dest='node',
							   help='delete node in the history of the project')

	# Reports in word
	report = subparsers.add_parser('report', help="Export the report in word format")
	report.add_argument('--excel', action='store_true', default=False,
						help="Generate a report in Excel")

	# Display readme file
	readme = subparsers.add_parser('readme', help="display readme file with instructions")

	# Parse arguments
	args = parser.parse_args()

	# Load library
	wf = pmlib.Workflow(settings.DATABASE_PATH)

	# Parse commands
	if args.command == 'status':
		wf.status(all=args.all, key=args.sort_key)


	elif args.command == 'history':
		if args.id == 0:
			max_id = max([project.id for project in wf.projects + wf.projects_done])
			for i in range(1, max_id):
				wf.history(i)
		else:
			wf.history(args.id)


	elif args.command == 'add':
		if args.type in settings.TYPE_OF_CONTRACTS:
			wf.add_project(args.name, args.type, args.money)
			wf.status()
		else:
			print("Error: type of contract must be {0}".format(
				', '.join(type_of_contract))
			)


	elif args.command == 'rm':
		wf.rm(args.id)


	elif args.command == 'stats':
		if args.all_year:
			args.start_date = None
			args.end_date = None
		if args.year:
			args.start_date = datetime.datetime.strptime('01/01/'+str(args.year), '%d/%m/%Y')
			args.end_date = datetime.datetime.strptime('31/12/'+str(args.year), '%d/%m/%Y')
		if not args.year and not args.all_year:
			year = datetime.date.today().year
			if args.start_date:
				args.start_date = datetime.datetime.strptime(args.start_date, '%d/%m/%Y')
			else:
				args.start_date = datetime.datetime.strptime('01/01/'+str(year), '%d/%m/%Y')
			if args.end_date:
				args.end_date = datetime.datetime.strptime(args.end_date, '%d/%m/%Y')
			else:
				args.end_date = datetime.datetime.strptime('31/12/'+str(year), '%d/%m/%Y')
		wf.stats(start_date=args.start_date, end_date=args.end_date)


	elif args.command == 'commit':
		if args.node:
			# Remove commit
			wf.rm_action(args.id, node=args.node)
		else:
			# Commit
			status_approved = settings.PROGRESS.keys()
			if args.status and args.status not in status_approved:
				print("Error, status must be: {0}".format(', '.join(status_approved)))
			else:
				wf.add_action(args.id, status=args.status, comment=args.commit)


	elif args.command == 'report':
		if args.excel:
			export.report_excel(wf)
		else:
			export.report_word(wf)


	elif args.command == 'update':
		project = wf.find_project(args.id)
		if args.name:
			project.name = args.name
		if args.type:
			project.type = args.type
		if args.money:
			project.money = args.money
		if args.money_year:
			project.money_year = args.money_year
		if args.summary:
			project.summary = args.summary
		if args.pi:
			project.pi = args.pi
		if args.ref:
			project.ref = args.ref
		wf.save()

	elif args.command == 'readme':
		export.open_file(settings.DIR + '/readme.md')

if __name__ == '__main__':
	main()

