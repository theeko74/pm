"""
This module include all class objects used
for the management project system MP.
"""

import json
import datetime
import copy

# Load settings of the lib
import settings

class Workflow:
	"""
	Workflow is the interface that manages all projects.
	"""

	def __init__(self, db_path):
		"""Initialization of the instance"""
		# Attributes
		self.db_path = db_path
		with open(self.db_path, 'r') as db:
			self.json = json.load(db)
		self.projects = []
		self.projects_done = []

		# Load
		for project in self.json['projects']:
			project_history_sorted = sorted(
				project['history'], key=lambda k: k['date']
			)
			project_obj = Project(
				project['name'], project['type'], project['money'],
				id=project['id'], history=project_history_sorted,
				money_year=project['money_year'], pi=project['pi'],
				summary=project['summary'], ref=project['ref']
			)
			if 'Done' not in [hist['status'] for hist in project['history']]:
				self.projects.append(project_obj)
			else:
				self.projects_done.append(project_obj)


	def sort_projects(self, key='date'):
		def sort(k):
			if key == 'date':
				return k.history[-1]['date']
			if key == 'status':
				return len(settings.PROGRESS[k.history[-1]['status']])
			if key == 'name':
				return k.name
			if key == 'ref':
				return k.ref
			if key == 'id':
				return k.id
			else:
				return getattr(k, key)
		self.projects = sorted(
			self.projects, key=sort, reverse=key not in ['id', 'name']
		)
		self.projects_done = sorted(
			self.projects_done, key=sort, reverse=key not in ['id', 'name']
		)


	def find_project(self, id):
		"""Return the project found in the workflow"""
		projects = self.projects + self.projects_done
		for project in projects:
			if project.id == id:
				return project


	def status(self, all=None, key='status'):
		"""Display all the projects ongoing"""

		# Sort projects
		self.sort_projects(key=key)
		
		# All projects vs ongoing projects only
		if all:
			temp_projects = self.projects_done + self.projects
		else:
			temp_projects = self.projects

		# Style
		print("-" * settings.WIDTH)

		# Display projects
		for project in temp_projects:
			project_last_node = project.history[-1]
			time_bet_action = (datetime.datetime.now() - project_last_node['date']).days + 1

			# Trunc comment if too long (>settings.WIDTH)
			comment = self.truncate(project_last_node['comment'])

			# Color
			color = ''
			end_color = ''
			if all and project.history[-1]["status"] == 'Done':
				color = '\033[92m'
				end_color = '\033[0m'
			else:
				if time_bet_action > settings.WARN_TIME:
					color = '\033[91m'
					end_color = '\033[0m'

			print(color + "#{id:<2} {name:<12}  {type:<4} |{progress:<6}| " \
				  "{comment}".format(
				id=project.id,
				name=project.name[:12],
				type=project.type,
				status=project_last_node['status'],
				progress=settings.PROGRESS[project_last_node['status']],
				date=datetime.datetime.strftime(
					project_last_node['date'], '%d/%m/%Y'
				),
				comment=comment
			) + end_color)
			
		print("-" * settings.WIDTH)

	
	@staticmethod
	def truncate(txt, width=settings.WIDTH, indent=32):
		import pdb
		tmp = ''
		output = []
		for index, word in enumerate(txt.split()):
			if len(tmp) + len(word) < width - indent:
				tmp += ' ' + word
				if index == len(txt.split()) - 1:
					output.append(tmp.strip())
					break
			else:
				output.append(tmp.strip()) 
				tmp = word
		return ('\n' + (' ' * indent)).join(output)



	def add_project(self, name, type, money):
		# Find id available
		ids = [project.id for project in self.projects + self.projects_done]
		new_id = max(ids) + 1 if ids else 1

		# Create new project
		new_project = Project(name, type, money, id=new_id, history=[])
		self.projects.append(new_project)
		self.sort_projects()
		self.save()


	def save(self):
		"""Write to database"""
		self.json["projects"] = [
			project.dumps() for project in self.projects + self.projects_done
		]
		with open(self.db_path, 'w') as db:
			json.dump(self.json, db, sort_keys=True, indent=4)	# Write JSON format to database


	def rm(self, id):
		"""Delete project of the database"""
		projects = [self.projects, self.projects_done]
		for project_data in projects:
			for project in project_data:
				if project.id == id:
					project_data.remove(project)
					self.save()
					print("{} was deleted".format(project))
					break
					break


	def add_action(self, id, status="", comment="-"):
		for project in self.projects:
			if project.id == id:
				if not status:
					status = project.history[-1]["status"]
				project.add_action(status, comment)
				self.save()
				if status == "Done":
					print("Congrats, one more project done !")
				else:
					self.history(id)
				break


	def rm_action(self, project_id, node=None):
		for project in self.projects + self.projects_done:
			if project.id == project_id:
				if node:
					project.del_action(int(node))
				else:
					# Delete last action
					project.del_action(project.history[-1]["node"])
				self.save()
				self.history(project_id)
				break


	def history(self, id):
		for project in self.projects + self.projects_done:
			if project.id == id:
				print("-" * settings.WIDTH)
				print("Project #{id:<2}  {name:<10} {type:<3}  {money:>4} kEUR  Duration:{duration:<9}".format(
					name=project.name,
					type=project.type,
					id=project.id,
					money=project.money,
					duration=self.duration(
						project.history[0]["date"], project.history[-1]["date"]
					)
				))
				if project.pi or project.money_year:
					print("             Current year:  {money_year:>5} kEUR  PI: {pi:<7}".format(
						pi=project.pi, money_year=project.money_year
					))
				if project.ref:
					print("             Ref: {ref:<12}".format(ref=project.ref))
				if project.summary:
					print("             {summary}".format(
						summary=self.truncate(project.summary, indent=13)
					))
					print("-" * settings.WIDTH)
				for index, hist in enumerate(project.history):
					if index == 0:
						days = '--'
					else:
						diff = hist['date'] - project.history[index-1]['date']
						days = str(diff.days) + 'd'
					print("  {node:>2}   {date:<11} {days:>5}  {status:<5} "\
						  "|{progress:<6}|  {comment:<35}".format(
						date=datetime.datetime.strftime(hist['date'], '%d/%m/%Y'),
						status=hist['status'],
						comment=self.truncate(hist['comment'], indent=42),
						progress=settings.PROGRESS[hist['status']],
						days=days,
						node=hist["node"]
					))
				print("-" * settings.WIDTH)
				break


	@staticmethod
	def duration(date_start, date_end):
		duration = date_end - date_start
		return Workflow.days_or_months(duration.days)


	@staticmethod
	def days_or_months(days):
		if days <= 31:
			return "{:3.0f} days".format(days)
		else:
			return "{:2.0f} months".format(days/30)


	def stats(self, start_date=None, end_date=None):

		# Make calculation of stats
		# Start and end date
		if not start_date:
			start_date = min([
				min([hist["date"] for hist in project.history]) \
				for project in self.projects + self.projects_done
			])
		if not end_date:
			end_date = max([
				max([hist["date"] for hist in project.history]) \
				for project in self.projects + self.projects_done
			])

		# Number of projects
		nb_projects = len([
			project for project in self.projects+self.projects_done \
			if start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date']
		])
		nb_active_projects = len([
			project for project in self.projects \
			if start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date']
		])
		nb_license = len([
			project.type for project in self.projects + self.projects_done \
			if (project.type == "Lic" or project.type == "aLic") \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		nb_license_ongoing = len([
			project.type for project in self.projects \
			if (project.type == "Lic" or project.type == "aLic") \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		nb_rnd = len([
			project.type for project in self.projects + self.projects_done \
			if (project.type == "R&D" or project.type == "aR&D" \
			or project.type == 'MTA' or project.type == 'aMTA') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		nb_rnd_ongoing = len([
			project.type for project in self.projects \
			if (project.type == "R&D" or project.type == "aR&D" \
			or project.type == 'MTA' or project.type == 'aMTA') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])

		# Money
		total_money_done = sum([
			project.money for project in self.projects_done \
			if start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date']
		])
		total_money_ongoing = sum([
			project.money for project in self.projects \
			if start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date']
		])
		total_money_year = sum([
			project.money_year for project in self.projects_done \
			if start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date']
		])
		total_money_license_signed = sum([
			project.money for project in self.projects_done \
			if (project.type == "Lic" or project.type == 'aLic') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		total_money_license_ongoing = sum([
			project.money for project in self.projects \
			if (project.type == "Lic" or project.type == 'aLic') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		total_money_rnd_signed = sum([
			project.money for project in self.projects_done \
			if (project.type == "R&D" or project.type == 'aR&D' \
			or project.type == 'MTA' or project.type == 'aMTA') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])
		total_money_rnd_ongoing = sum([
			project.money for project in self.projects \
			if (project.type == "R&D" or project.type == 'aR&D' \
			or project.type == 'MTA' or project.type == 'aMTA') \
			and (start_date <= project.history[-1]['date'] \
			and end_date >= project.history[0]['date'])
		])

		# Deal with Zerodivision
		if nb_projects > 0 and (nb_projects - nb_active_projects) > 0:

			# Time to done performance
			time_to_done = sum([
				(project.history[-1]["date"] -  project.history[0]["date"]).days \
				for project in self.projects_done \
				if start_date <= project.history[-1]['date'] \
				or end_date <= project.history[0]['date']
			]) / (nb_projects - nb_active_projects)

			cash_per_project = (total_money_done + total_money_ongoing) / nb_projects
			cash_per_license = (total_money_license_signed + total_money_license_ongoing) / nb_license
			cash_per_rnd = (total_money_rnd_signed + total_money_rnd_ongoing) / nb_rnd

		else:
			time_to_done = 0.0
			cash_per_project = 0.0
			cash_per_license = 0.0
			cash_per_rnd = 0.0

		# Print
		WIDTH = settings.WIDTH - 30
		
		print("-" * WIDTH)
		
		print("  User: S.CARLIOZ")
		print("  Stats from {0} to {1}".format(
			datetime.datetime.strftime(start_date, '%d/%m/%Y'),
			datetime.datetime.strftime(end_date, '%d/%m/%Y'))
		)

		print("-" * WIDTH)

		print("  Total amount signed........ {0:>4} kEUR".format(total_money_done))
		print("     * Licenses.............. {0:>4} kEUR".format(total_money_license_signed))
		print("     * R&D/MTA............... {0:>4} kEUR".format(total_money_rnd_signed))
		print("  Total invoiced this year... {0:>4} kEUR".format(total_money_year))

		print("  Total amount in nego....... {0:>4} kEUR".format(total_money_ongoing))
		print("     * Licenses.............. {0:>4} kEUR".format(total_money_license_ongoing))
		print("     * R&D/MTA............... {0:>4} kEUR".format(total_money_rnd_ongoing))

		
		
		print("-" * WIDTH)

		print("  Cash per project........... {0:>4.0f} kEUR".format(cash_per_project))
		print("  Cash per license........... {0:>4.0f} kEUR".format(cash_per_license))
		print("  Cash per R&D............... {0:>4.0f} kEUR".format(cash_per_rnd))

		print("-" * WIDTH)

		print("  Number of projects")
		print("     * Total.................. {0}".format(nb_projects))
		print("     * Signed................. {0}".format(nb_projects-nb_active_projects))
		print("     * Active................. {0}".format(nb_active_projects))
		print("  Number of licenses")
		print("     * Total.................. {0}".format(nb_license))
		print("     * Signed................. {0}".format(nb_license-nb_license_ongoing))
		print("     * Active................. {0}".format(nb_license_ongoing))
		print("  Number of R&D")
		print("     * Total.................. {0}".format(nb_rnd))
		print("     * Signed................. {0}".format(nb_rnd-nb_rnd_ongoing))
		print("     * Active................. {0}".format(nb_rnd_ongoing))
		print("-" * WIDTH)
		print("  Average time to Done........ {0}".format(
			self.days_or_months(time_to_done)
		))
		print("-" * WIDTH)



class Project:

	def __init__(self, name, type, money,
				 money_year=0, id=0, history=[], pi="", summary="", ref=""):
		self.id = id
		self.ref = ref
		self.name = name
		self.type = type
		self.money = money
		self.money_year = money_year
		self.pi = pi
		self.summary = summary
		self.history = history
		if self.history:
			for hist in self.history:
				hist['date'] = datetime.datetime.strptime(
					hist['date'], '%Y-%m-%dT%H:%M:%S.%f'
				)
		else:
			self.history.append({
				"node": 1,
				"status": "Start",
				"date": datetime.datetime.now(),
				"comment": "-"
			})


	def __repr__(self):
		return "Project: {name:<10} {type:<3} {money:>5} kEUR".format(
			name=self.name, type=self.type, money=self.money
		)


	def dumps(self):
		"""Convert Project object to JSON"""
		# Copy history
		history = copy.deepcopy(self.history)	# Slow method
		for hist in history:
			hist['date'] = hist['date'].isoformat()
		#print(history)

		#JSON
		return {
			"id": self.id,
			"name": self.name,
			"type": self.type,
			"money": self.money,
			"money_year": self.money_year,
			"pi": self.pi,
			"ref": self.ref,
			"summary": self.summary,
			"history": history
		}


	def add_action(self, status, comment):
		"""Add an action to the project"""
		new_node = self.history[-1]['node'] + 1
		self.history.append({
			"node": new_node,
			"status": status,
			"date": datetime.datetime.now(),
			"comment": comment
		})


	def del_action(self, node):
		for hist in self.history:
			if hist["node"] == node:
				self.history.remove(hist)
				break






