#!/usr/bin/python

import pygtk
pygtk.require('2.0')

import gtk
import os
import shutil
import time
import locale

# Pass backup a source and target and it will attempt to identify
# whether or not a windows installation is present, and if so,
# it will attempt to then backup the user and driver folders

class Backup:
	def __init__(self, source, target):
		self.source = source
		self.target = target
		self.users = []
		self.copying = True
		self.important_folders = []
	
	def valid_directories(self):
		return (os.path.exists(self.source) and 
		        os.path.exists(self.target))
		        
	def get_dir_size(self,root):
		size = 0
		for path, dirs, files in os.walk(root):
			for f in files:
				size +=  os.path.getsize( os.path.join( path, f ) )
		return size
    
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
			return ["Desktop", "Favorites", "My Documents"] 
    	
    #pretty file size :)
	def pfs(self, bytes):
		suffix = "B"
		if(bytes > 999 and bytes <= 999999 ):
			suffix = "KB"
			bytes = bytes / 1000
		elif(bytes > 999999 and bytes <= 999999999):
			suffix = "MB"
			bytes = bytes / 1000000
		elif(bytes > 999999999):
			suffix = "GB"
			bytes = bytes / 1000000000
		
		return locale.format("%d", bytes, grouping=True) + suffix
		
	def cancel_copy(self, widget=None):
		self.copying = False
		
	def copy(self, src, dest, callback):
		if(not self.copying):
			return
			
		try:
			fin = open(src, 'rb')
			fout = open(dest, 'wb')
			
			#Set up reporting
			self.copy_size = os.path.getsize(src)
			self.copy_progress = 0
			self.copy_percent = 0
			self.copy_folder_from = os.path.split(src)[0]
			self.copy_folder_to = os.path.split(dest)[0]
			
			if(len(self.copy_folder_from) > 50 ):
				self.copy_folder_from = '...' + self.copy_folder_from[-47:]
			if(len(self.copy_folder_to) > 50 ):
				self.copy_folder_to = '...' + self.copy_folder_to[-47:]
			
			self.copy_filename = os.path.split(src)[1]
			self.display_string = 'User: ' + self.copy_user + '\nFrom: ' + self.copy_folder_from + '\nTo: ' + self.copy_folder_to + '\nFile: ' + self.copy_filename
			try:
				callback(self.copy_percent, self.display_string + '\nProgress: 0%')
				chunk = fin.read(4096)
				while chunk != "":
					callback(self.copy_percent, self.display_string + '\nProgress: ' + str(int(100*self.copy_percent)) + '%')
					if(not self.copying):
						return
					self.copy_progress = self.copy_progress + len(chunk)								
					fout.write(chunk)
					chunk = fin.read(4096)
					self.copy_percent = float(self.copy_progress) / float(self.copy_size)
			
			finally:
				fin.close()
				fout.close()
		except IOError:
			print 'Error: source file does not exist.\n'
			
	def cptree(self, src, dst, callback=None):
			
		names = os.listdir(src)
		os.makedirs(dst)
		
		for name in names:
			if(not self.copying):
				return
				
			srcname = os.path.join(src, name)
			dstname = os.path.join(dst, name)
			
			if(os.path.isdir(srcname)):
				self.cptree(srcname, dstname, callback)
			else:
				if(os.path.islink(srcname)):
					continue #eff symlinks!			
				else:				
					self.copy(srcname, dstname, callback)
					
	def get_dir_size(self, target):
		names = os.listdir(target)
		size  = 0
		
		for name in names:
			targetname = os.path.join(target,name)
			if(os.path.isdir(targetname)):
				size = size + self.get_dir_size(targetname)
			else:
				size = size + os.path.getsize(targetname)
		
		return size
		
	@staticmethod
	def determine_winver(src):
		winver = None
		
		# Checking the directory structure should give us a general
		# idea.
		if(os.path.exists(os.path.join(src,'Users'))):
			winver = '7'
		elif(os.path.exists(os.path.join(src, 'Documents and Settings'))):
			winver = 'xp'
		
		# Let's give the ol' boot.ini a looksee.
		try:
			bootini = open(os.path.join(src, 'boot.ini'))
			if(bootini):
				contents = bootini.read()
				if(contents.find('XP') != -1):
					winver = 'xp'
				elif(contents.find('Vista') != -1):
					winver = 'vista'
				elif(contents.find('Windows 7')):
					winver = '7'
			bootini.close()	
		except IOError:
			None 

		return winver
				
	def get_user_folder_loc(self, src, winver):
		if(winver == '7' or winver == 'vista'):
				return os.path.join(src, 'Users')
		elif(winver == 'xp'):
			return os.path.join(src, 'Documents and Settings')
		else:
			return None
	
	def commence(self, update_callback=None):
		# The search begins		
		winver = Backup.determine_winver(self.source)
		user_folder_loc = self.get_user_folder_loc(self.source, winver)
			
		if(not user_folder_loc == None and self.populate_users(user_folder_loc)):
			self.important_folders = self.get_important_folders(winver)
			
			for user in self.users:
				self.copy_user = user

				for folder in self.important_folders:
					copy_src = os.path.join(user_folder_loc, user,folder)
					copy_dst = os.path.join(self.target, user, folder)
					
					if(os.path.isdir(copy_src) 
					   and not os.path.isdir(copy_dst)):		
									
						self.copy_folder_name = folder
						self.cptree(copy_src, copy_dst, callback=update_callback)
						
						if(not self.copying):
							return					
				
			return True
		else:
			print 'Error: found no user folders in /Users\n'
			return	False

class Application:
	
	def dialog_on_click(self, widget, data=None):
		if(data != None):
			if(data == "source"):
				self.source = self.generate_source_chooser()
			elif(data == "target"):
				self.target = self.generate_target_chooser()	
			
		
	def delete_event(self, widget, event, data=None):
		if(self.backup):
			self.backup.cancel_copy(None)
			
		return False
		
	def destroy(self, widget, data=None):
		if(self.backup):
			self.backup.cancel_copy(None)
			
		gtk.main_quit()
		return
		
	def source_response (self, widget, response):
		if(response == gtk.RESPONSE_OK):
			self.source_dir = self.source.get_filename()
			winver = Backup.determine_winver(self.source_dir)
			if(winver == 'xp'): winver = "Windows XP"
			elif(winver == 'vista'): winver = "Windows Vista"
			elif(winver == '7'): winver = "Windows 7"
			
			self.source_label.set_text(self.source.get_filename() + '\nOS detected: ' + winver)
						
		self.source.hide()
		
	def target_response(self, widget, response):
		if(response == gtk.RESPONSE_OK):
			self.target_label.set_text(self.target.get_filename())
			self.target_dir = self.target.get_filename()
		self.target.hide()
	
	def update_dialog_callback(self, percent, displaystring):
		while gtk.events_pending():
		   gtk.main_iteration(False)
		
		self.progbar.set_fraction(float(percent))
		self.progbar.set_text(displaystring)

	def prog_destroy(self, widget, backup):		
		backup.cancel_copy()
		

	def commence_ze_copy(self, widget, data=None):
		self.copy_button.set_label("Copying...")
		
		self.backup = Backup(self.source_dir,
		                     self.target_dir)
		                     
		# Let's verify that these are valid directories, and if not
		# alert the user of their error.
		if(not self.backup.valid_directories()):
			print 'Hey, stupid, these aren\'t directories.'
		else:
			self.progdia = self.generate_progdia()
			
			self.cancel_button.connect("clicked", self.backup.cancel_copy)
			self.progdia.connect("destroy", self.prog_destroy, self.backup)
		
			self.backup.commence(update_callback=self.update_dialog_callback)
						
			if(self.backup.copying):
				self.progbar.set_fraction(float(1.0))
				self.progbar.set_text("Copy complete!")
			else:
				self.progbar.set_fraction(float(0.0))
				self.progbar.set_text("Copy Cancelled!")
				
			self.copy_button.set_label("Copy")
			self.progdia = None
			
				
		self.copy_button.set_label("Copy")
		self.backup = None
	
	def generate_source_chooser(self):
		self.source  = gtk.FileChooserDialog('Select a directory to pull from...', 
											None,
											gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
											buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
											           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

		self.source.connect("response", self.source_response)
		self.source.show()
		self.source.set_modal(True)
				
		return self.source

	def generate_target_chooser(self):	
		self.target  = gtk.FileChooserDialog('Select a directory to backup into...', 
											None,
											gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
											buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_OK,
											           gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
											           
		self.target.connect("response", self.target_response)
		self.target.show()
		self.source.set_modal(True)
				
		return self.target

	def generate_progdia(self):
		self.progdia = gtk.Dialog('Copying...', buttons = None)
		self.progdia.set_geometry_hints(min_width = 600, min_height = 150, max_width = 600, max_height = 150)
		self.progdia.set_modal(True)
		self.progbar = gtk.ProgressBar()
		self.cancel_button = gtk.Button('Cancel')
		self.progdia.set_default_size(600,100)
		self.progdia.set_resizable(False)
		self.progtable = gtk.Table(rows=2, columns=4, homogeneous=False)
		self.progtable.set_row_spacings(10)
		self.progtable.attach(self.progbar, 0, 4, 0, 1)
		self.progtable.attach(self.cancel_button, 3, 4, 1, 2)
		self.progdia.vbox.pack_start(self.progtable, True, True, 0)
		self.progdia.show()
		self.progbar.show()
		self.cancel_button.show()
		self.progtable.show()
	
		return self.progdia
	
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.set_border_width(10)
		self.window.set_title("PCPickup Customer Backup")
		self.window.set_default_size(300,100)
		self.window.set_resizable(False)
		self.backup = None
		self.progdia = None
		self.source = None
		self.target = None
				
		# Setup buttons
		self.source_button = gtk.Button('Source')
		self.target_button = gtk.Button('Target')
		self.copy_button = gtk.Button('Copy')
		
		self.source_button.connect("clicked", self.dialog_on_click, "source");
		self.target_button.connect("clicked", self.dialog_on_click, "target");
		self.copy_button.connect("clicked", self.commence_ze_copy)
		
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
		
		# Main Table Layout
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
