from docxtpl import DocxTemplate
import jinja2
import settings
from datetime import datetime
import os
import xlsxwriter


def report_context(workflow, all=False):
	"""
	Function to generate the context elements to be insert in a nice report.
	"""
	projects_context = []
	now = datetime.now()
	workflow.sort_projects(key='status')

	projects = workflow.projects
	if all:
		projects += workflow.projects_done

	for project in projects:
		# Progress bar
		cell1 = cell2 = cell3 = cell4 = cell5 = cell6 = 'ffffff'
		progress = len(settings.PROGRESS[project.history[-1]['status']])
		if progress > 0:
			cell1 = settings.WORD_COLOR_CELL
		if progress > 1:
			cell2 = settings.WORD_COLOR_CELL
		if progress > 2:
			cell3 = settings.WORD_COLOR_CELL
		if progress > 3:
			cell4 = settings.WORD_COLOR_CELL
		if progress > 4:
			cell5 = settings.WORD_COLOR_CELL
		if progress > 5:
			cell6 = settings.WORD_COLOR_CELL

		# Context
		projects_context_temp = {
			'name': project.name,
			'type': project.type.replace('&', 'n'),
			'euro': project.money if project.money > 0 else '-',
			'comment': project.history[-1]['comment'],
			'cell1': cell1,
			'cell2': cell2,
			'cell3': cell3,
			'cell4': cell4,
			'cell5': cell5,
			'cell6': cell6
		}

		projects_context.append(projects_context_temp)

	context = {
		'date': now.strftime('%d/%m/%Y'),
		'projects': projects_context
	}

	return context



def report_word(workflow, all=False):
	"""
	Function to generate a word report.
	"""
	now = datetime.now()
	# Get context
	context = report_context(workflow, all=all)

	# Generate template
	tpl = DocxTemplate(settings.DIR + '/' + settings.WORD_TEMPLATE)
	tpl.render(context)
	
	# Make directory if it does not exist yet
	if not os.path.exists(settings.DIR + "/Reports"):
		os.makedirs(settings.DIR + "/Reports")

	# Generate file name and save the doc
	file_name = settings.DIR + '/Reports/Suivi_SC_' + str(now.month) + '_' + str(now.year) + '.docx'
	tpl.save(file_name)
	
	# Open the word file
	open_file(file_name)

def open_file(file_path):
	"""Function to open a file with the default application and based on the OS platform"""
	if os.name == 'posix':
		os.system("open " + file_path)
	else:
		os.system("start " + file_path)


def report_excel(workflow, all=False):
	"""Function to make a report of the current projects on a Excel sheet"""

	# Initi and start excel sheet
	now = datetime.now()
	path_name = settings.DIR + '/Reports/Suivi_SC_Excel_' + str(now.month) + '_' + str(now.year) + '.xlsx'
	wb = xlsxwriter.Workbook(path_name)
	ws = wb.add_worksheet()

	# Sorts projects and get data
	workflow.sort_projects(key='name')
	projects = workflow.projects
	if all:
		projects += workflow.projects_done

	# Headers
	ws.write(0, 0, "Person in charge")
	ws.write(0, 1, "Type of contract")
	ws.write(0, 2, "Company")
	ws.write(0, 3, "Summary")
	ws.write(0, 4, "-")
	ws.write(0, 5, "-")
	ws.write(0, 6, "-")
	ws.write(0, 7, "PI")
	ws.write(0, 8, "Status")
	ws.write(0, 9, "EUR 1st year")
	ws.write(0, 10, "EUR pot.")
	ws.write(0, 11, "Ref")


	# Loop over projects
	row = 1
	col = 0
	for project in projects:

		# Convert to French
		status_translate = {
			'Start': '1 - Prospection',
			'Progr': '2 - Programme scientifique',
			'Budge': '3 - Budget',
			'Contr': '4 - Négociation contrat',
			'Sign':  '5 - Signature / Suivi'
		}
		contracts_translate = {
			'R&D':  'Collab R&D',
			'aR&D': 'Collab R&D',
			'Lic':  'Licence',
			'aLic': 'Licence',
			'MTA':  'Collab R&D'
		}

		# Write in the excel sheet
		ws.write(row, col, "Sylvain CARLIOZ")
		ws.write(row, col + 1, contracts_translate[project.type])
		ws.write(row, col + 2, project.name)
		ws.write(row, col + 3, project.summary)
		ws.write(row, col + 7, project.pi)
		ws.write(row, col + 8, status_translate[project.history[-1]['status']])
		ws.write(row, col + 9, project.money_year * 1000)
		ws.write(row, col + 10, project.money * 1000)
		ws.write(row, col + 11, project.ref)
		row += 1

	# Close excel sheet
	wb.close()

	# Open with default app
	open_file(path_name)