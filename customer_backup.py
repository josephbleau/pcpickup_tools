#!/usr/bin/python

import pygtk
pygtk.require('2.0')

import gtk
import os
import shutil


# Pass backup a source and target and it will attempt to identify
# whether or not a windows installation is present, and if so,
# it will attempt to then backup the user and driver folders

class Backup:
	def __init__(self, source, target):
		self.source = source
		self.target = target
		self.users = []
		self.important_folders = []
	
	def valid_directories(self):
		return (os.path.exists(self.source) and 
		        os.path.exists(self.target))
	
	def populate_users(self, path):
		dirlist = os.listdir(path)
		
		for item in dirlist:
			if(os.path.isdir(path + '/' + item)):
				self.users = self.users + [item]
		
		return len(self.users)
	
	def get_important_folders(self, version):
		if(version == '7' or version == 'vista'):
			return ["Contacts", "Desktop","Documents", "Downloads",
				     "Favorites", "Links", "Music", "Pictures", 
				     "Videos"]
		if(version == 'xp'):
			return []  #todo, implement
	
	def commence(self):
		# The search begins		
		if(os.path.exists(self.source + '/Users')):
			path = self.source + '/Users'

			if(self.populate_users(path)):
				self.important_folders = self.get_important_folders('7')
				
				for user in self.users:
					for folder in self.important_folders:
						copy_src = path + '/' + user + '/' + folder
						copy_dst =  self.target + '/' + user + '/' + folder
						
						if(os.path.isdir(copy_src) 
						   and not os.path.isdir(copy_dst)):
							shutil.copytree(copy_src, copy_dst)
						
					
				return True
			else:
				print 'Error: found no user folders in /Users\n'
				return		
		elif(os.path.exists(self.source + '/Documents and Settings')):
			None #Todo, implement XP style folder scheme and refactor
			     #code above.

class Application:
	
	# Event Handlers 
	def dialog_on_click(self, widget, data=None):
		data.show()
		
	def delete_event(self, widget, event, data=None):
		return False
		
	def destroy(self, widget, data=None):
		gtk.main_quit()
		
	def source_response (self, widget, response):
		if(response == gtk.RESPONSE_OK):
			self.source_label.set_text(self.source.get_filename())
		self.source.hide()
		
	def target_response(self, widget, response):
		if(response == gtk.RESPONSE_OK):
			self.target_label.set_text(self.target.get_filename())
		self.target.hide()
		
	def commence_ze_copy(self, widget, data=None):
		self.copy_button.set_label("Copying...")
		
		self.backup = Backup(self.source_label.get_text(),
		                     self.target_label.get_text())
		                     
		# Let's verify that these are valid directories, and if not
		# alert the user of their error.
		if(not self.backup.valid_directories()):
			print 'Hey, stupid, these aren\'t directories.'
		else:
			if(self.backup.commence() == True):
				comp_dia = gtk.Dialog('Status report:', buttons = None)
				comp_label = gtk.Label("Copy completed successfuly!")
				comp_dia.vbox.pack_start(comp_label, True, True, 0)
				comp_label.show()
				comp_dia.show()
				
		self.copy_button.set_label("Copy")
		
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.set_border_width(10)
		self.window.set_title("PCPickup Customer Backup")
		self.window.set_default_size(300,100)
		self.window.set_resizable(False)
				
		# Setup file choosers.
		self.source  = gtk.FileChooserDialog('Select a directory to pull from...', 
											None,
											gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
											buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
											           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		
		self.target  = gtk.FileChooserDialog('Select a directory to backup into...', 
											None,
											gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
											buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
											           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
											           
		self.source.connect("response", self.source_response)
		self.target.connect("response", self.target_response)
		
		# Setup buttons
		self.source_button = gtk.Button('Source')
		self.target_button = gtk.Button('Target')
		self.copy_button = gtk.Button('Copy')
		
		self.source_button.connect("clicked", self.dialog_on_click, self.source);
		self.target_button.connect("clicked", self.dialog_on_click, self.target);
		self.copy_button.connect("clicked", self.commence_ze_copy, None)
				
		#  Path labels
		self.source_label = gtk.Label("Select a source path:")
		self.target_label = gtk.Label("Select a target path:")
	
		# Program description label
		self.desc_label = gtk.Label('Point the source folder at any mounted\n'+
		                            'drive with a windows installation. The\n'+
		                            'application will attempt to\n'+ 
		                            'automatically determine the version of\n'+
		                            'windows and will then backup the\n'+
		                            'appropriate user folders as well as\n'+
		                            'common driver folder locations for\n'+ 
		                            'various OEMs.\n')
		                            
	
		# Table Layout
		self.table = gtk.Table(rows=4, columns=2, homogeneous=False)
		self.table.set_row_spacings(10)
		self.table.attach(self.source_label,  0,1,1,2)
		self.table.attach(self.target_label,  0,1,2,3)
		self.table.attach(self.source_button, 1,2,1,2)
		self.table.attach(self.target_button, 1,2,2,3)
		self.table.attach(self.copy_button, 0,2,3,4)
		self.table.attach(self.desc_label, 0,2,0,1)
		
		self.window.add(self.table)
		
		# .show() everything
		self.table.show()
		self.source_label.show()
		self.target_label.show()
		self.source_button.show()
		self.target_button.show()
		self.copy_button.show()
		self.desc_label.show()
		self.window.show()
		
	def main(self):
		gtk.main()
		
		
if __name__ == '__main__':
	app = Application()
	app.main()
