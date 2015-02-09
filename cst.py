#!/usr/bin/python

#CST:xkubov02

import string, sys, re, os, glob, codecs
from fnmatch import fnmatch

#########################
#Spracovanie parametrov
#########################
class handleParams:
	'Spracuje parametre z prikazoveho riadku'

	def __init__(self):
		#premenne pre detekciu parametrov
		self.infile = ''
		self.infilec = 0
		self.is_dir = False
		self.outfile = ''
		self.outfilec = 0
		self.filetype = ''
		self.nosub = 0
		self.keywords = 0
		self.operators = 0
		self.identifiers = 0
		self.pattern = ''
		self.patternc = 0
		self.comments = 0
		self.path = 0
		self.comb = 0
		self.argc = len(sys.argv)	#pocet zadanych parametrov
		self.com = 0

	#metoda zabezpecujuca parsovanie a detekciu parametrov
	def handle(self):
		if(self.argc > 7):
			sys.stderr.write("Neplatny pocet parametrov\n")
			sys.exit(1)
		else:
			for i in range(1,self.argc):
				
				#spracovanie parametru --help
				#nesmie byt zadany v kombinacii s ostatnymi parametrami
				if(sys.argv[i] == "--help" and self.argc != 2):
					sys.stderr.write("Help nebol zadany samostatne\n")
					sys.exit(1)
				elif(sys.argv[1] == "--help" and self.argc == 2):
					self.printHelp()
					sys.exit(0)

				pos = sys.argv[i].find("--input=")
				pos2 = sys.argv[i].find("--output=")
				pos3 = sys.argv[i].find("-w=")				

				#parameter --input
				#nacita vstupny subor pokial este nebol zadany
				if(self.infile == '' and pos != -1):
					if(pos == 0):
						self.infile = sys.argv[i][8:]		#ulozim si meno suboru

						#zistim ci sa jedna o adresar
						if(os.path.isdir(self.infile)):
							self.is_dir = True

						self.infilec = self.infilec + 1;
					else:
						sys.stderr.write("Chybny format parametru --input\n")
						sys.exit(1)

				#parameter --nosubdir
				elif(sys.argv[i] == "--nosubdir"):
					self.nosub = self.nosub + 1

				#parameter --output
				elif(self.outfile == '' and pos2 != -1):
					if(pos2 == 0):
						self.outfile = sys.argv[i][9:]	#ulozim si meno suboru
					else:
						sys.stderr.write("Chybny format parametru --output\n")
						sys.exit(1)
						sys.exit(1)

					self.outfilec = self.outfilec + 1

				#parameter -k
				elif(sys.argv[i] == "-k"):
					if(self.keywords == 0):
						self.comb = self.comb + 1
					self.keywords = self.keywords + 1

				#parameter -o
				elif(sys.argv[i] == "-o"):
					if(self.operators == 0):
						self.comb = self.comb + 1
					self.operators = self.operators + 1

				#parameter -i
				elif(sys.argv[i] == "-i"):
					if(self.identifiers == 0):
						self.comb = self.comb + 1
					self.identifiers = self.identifiers + 1

				#parameter -w
				elif(pos3 == 0):
					if(self.patternc == 0):
						self.comb = self.comb + 1
					self.pattern = sys.argv[i][3:]
					self.patternc = self.patternc + 1

				#parameter -c
				elif(sys.argv[i] == "-c"):
					if(self.comments == 0):
						self.comb = self.comb + 1
					self.comments = self.comments + 1

				#parameter -p
				elif(sys.argv[i] == "-p"):
					self.path = self.path + 1

				#parameter -s
				elif(sys.argv[i] == "-s"):
					self.com = self.com + 1					

				else:
					sys.stderr.write("Neplatny parameter\n")
					sys.exit(1)

			#osetrenie pripadu --nosubdir a konkretny subor
			if(self.nosub == 1 and self.is_dir == 0):
				sys.stderr.write("Neplatna kombinacia --nosubdir a konkretneho suboru --input\n")
				sys.exit(1)

			#osetrenie pripadu inych pripadov ako -s -c , je implementovane iba rozsirenie COM 
			if(self.com == 1 and self.comments != 1):
				sys.stderr.write("Pre rozsirenie COM nie je povolena ina kombinacia parametra -s ako -s -c\n")
				sys.exit(1)

			#osetrenie duplicity parametrov
			if (self.infilec > 1 or self.outfilec > 1 or self.nosub > 1 or self.keywords > 1 or self.operators > 1 or 
				self.identifiers > 1 or self.patternc > 1 or self.comments > 1 or self.path > 1 or self.com > 1):
				sys.stderr.write("Duplicitny parameter\n")
				sys.exit(1)

			#osetrenie neplatnej kombinacie parametrov -k -o -i -w -c
			if(self.comb > 1):
				sys.stderr.write("Parametre -k -o -i -w -c nemozno kombinovat\n")
				sys.exit(1)

	#vypise 
	def printHelp(self):
		msg = (	"****************C Stats**************************\n"
				"Projekt c.2 do predmetu IPP, VUT FIT 2012/2013\n"
				"Autor:\t\tTomas Kubovcik, xkubov02@stud.fit.vutbr.cz\n"
				"Popis:\t\tProgram vypise statistiky zvolenych dat v zdrojovych suboroch jazyka c\n"
				"Parametre:\n"
				" --input=fileordir\t- vstupny subor, alebo priecinok zo zdrojovymi subormi\n"
				" --output=file\t\t- vystupny subor\n"
				" --nosubdir\t\t- zakaze rekurzivne prehladavanie podpriecinkov na zdrojove subory\n"
				" -k\t\t\t- vyhlada klucove slova\n"
				" -i\t\t\t- vyhlada identifikatory\n"
				" -o\t\t\t- vyhlada operatory\n"
				" -w=pattern\t\t- vyhlada presne zadane slovo (pattern)\n"
				" -c\t\t\t- vyhlada komentare\n"
				" -p\t\t\t- nevypisuje absolutne cesty k suborom, iba mena suborov\n")

		sys.stdout.write(msg)

###################################################
#Detekuje pozadovane elementy v zdrojovych suboroch
###################################################
class find:
	'Spracuje parametre z prikazoveho riadku'

	def __init__(self):
		self.kwords = (	"auto","break","case","char","const","continue","default","do","double",
						"else","enum","extern","float","for","goto","if","int","long","register",
						"return","short","signed","sizeof","static","struct","switch","typedef",
						"union","unsigned","void","volatile","while","inline","restrict"
						)
		self.operators = (	"[^\+]\+[^\+=]", "[^&]&[^&=]", "[^\.>]\*[^=]", "\+\+", "--", "%[^=]",
							"[^>]>=", "==", "!=", "\^[^=]", "[^\|]\|[^\|=]", "&&", "\|\|", "\/[^=]",
							"\|=", ">>=",  "<<=", "\^=", "[^\*=<>!\+-\/%&\^\|\]]=[^=]",
							"[a-zA-Z_]\w*\.[a-zA-Z_]\w*", "->[^\*]", "![^=]", "~", "[^-]-[^->=]",
							"<<[^=]", ">>[^=]", "[^<]<[^<=]", "[^<]<=", "[^>-]>[^>=*]",
							"\+=", "-=", "\*=", "\/=", "%=", "&="
							)

		self.multiline_macro = False
		self.mline_comment = False
		self.mline_literal = False
		self.mix = []
		self.onefile = ''

	def handleFile(self,subor,f,root):
			count = 0		#pocitadlo najdenych elementov

			while(1):
				line = subor.readline();		#nacita riadok zo suboru

				#ak som docital, ukoncim cyklus
				if(line == ""):
					break

				#vyhlada klucove slova
				if(params.keywords > 0):
					line = remove.chars(line)	
					line = remove.strings(line)
					line = remove.comments(line)					
					line = remove.gridElements(line)						
					
					#vyfiltruje klucove slova
					for i in range(len(self.kwords)):
						result = re.findall('\W' + self.kwords[i] + '\W|^' + self.kwords[i] + '\W|^' + self.kwords[i] + '$|\W' + self.kwords[i] + '$',line)
						count = count + len(result)

				#vyhlada operatory
				if(params.operators > 0):
					line = remove.chars(line)					
					line = remove.strings(line)
					line = remove.comments(line)
					line = remove.gridElements(line)

					#vyfiltruje operatory
					for i in range(len(self.operators)):
						found = re.findall(self.operators[i],line)

						count += len(found)

				#vyhlada identifikatory
				elif(params.identifiers > 0):
					line = remove.chars(line)
					line = remove.strings(line)					
					line = remove.comments(line)
					line = remove.gridElements(line)					        	

					cnt = 0    	

					#vyhlada vsetky slova podla regexp na danom riadku, zahrnuje klucove slova
					found = re.findall("[_A-Za-z][_A-Za-z0-9]*",line)

					#vyfiltrujeme vysledok klucovymi slovami
					for i in range(len(found)):
						if(found[i] in self.kwords):
							pass
						else:
							cnt += 1

					count += cnt

				#vyhlada pattern
				elif(params.patternc > 0):

					result = re.findall(params.pattern,line)	#vyhlada vsetky slova podla vzoru na danom riadku
					count += len(result)						#vrati dlzku zoznamu

				#vyhlada komentare
				elif(params.comments > 0):

					#COM: ak je zadany prepinac -s, pocitame aj v makrach
					if(params.com > 0):
						line = line.rstrip()
					else:
						line = remove.gridElements(line)
					
					#ak sa multiriadkovy komentar na riadku ukoncuje, nepripocitavam +1
					if(line.find("*/") != -1):
						endcmnt = 1
					else:
						endcmnt = 0			        			

					len_w_comment = len(line)		#uchovam si dlzku riadku s komentarmi
					#tmp = line
					line = remove.comments(line)	#odstranim komentare
					len_wo_comment = len(line)		#uchovam si dlzku bez komentarov

					if(len_w_comment != len_wo_comment):

						if(self.mline_comment == False and endcmnt == 0):	#telo jedno/viacriadkoveho komentaru (pripocitavam +1 (\n))
							count += (len_w_comment - len_wo_comment) + 1
							#print(tmp,count)
						elif(self.mline_comment == False and endcmnt == 1):	#koniec viacriadkoveho komentaru (nepripocitavam +1 (\n))
							count += (len_w_comment - len_wo_comment)        					
							#print(tmp,count)
						elif(self.mline_comment == True):
							count += (len_w_comment - len_wo_comment) + 1	#telo viacriadkoveho komentaru, + 1 ako len('\n')
							#print(tmp,count)
													
			#overi ci bol zadany parameter -p
			if(params.path == 0 and params.nosub > 0):	
				self.onefile = (os.path.abspath(f), count)				
			elif(params.path > 0):
				self.onefile = (f, count)
			elif(params.path == 0 and params.nosub == 0):
				self.onefile = (os.path.abspath(root), count)

			self.mix.append(self.onefile) 	        

	def FindElements(self,params):
		root = params.infile
		ext = "*.c"
		ext2 = "*.h"
		endcmnt = 0
		files = []
		wd = os.getcwd()
		rootx = root

		#nebol zadany vstupny subor, nastavime na aktualny adresar
		if(params.infilec == 0):
			root = '.'

		#vstupny subor je priecinok a nieje pozadovany rekurzivny priechod
		if(params.is_dir == True and params.nosub == 1):
			os.chdir(root)	#presuniem sa do aresara

			files = filter(os.path.isfile, os.listdir('.'))	#vyfiltrujem priecinky a ziskam subory

			for f in files:
				if(f.endswith(".c") or f.endswith(".h")):
					try:
						subor = open(f)
					except IOError:
						sys.stderr.write("Nepodarilo sa otvorit vstupny subor\n")
						sys.exit(2)

					root = os.path.join(rootx,f)

					self.handleFile(subor,f,root)
					subor.close

			os.chdir(wd)	#presuniem sa do povodneho adresara

		#vstupny subor je priecinok a je pozadovany rekurzivny priechod					
		elif((params.is_dir == True and params.nosub == 0) or (params.infilec == 0)):

			for path, subdirs, files in os.walk(root):
				for name in files:
					if(fnmatch(name, ext) or fnmatch(name, ext2)):
						try:
							subor = open(os.path.join(path, name))
						except IOError:
							sys.stderr.write("Nepodarilo sa otvorit vstupny subor\n")
							sys.exit(2)

						root = os.path.join(path,name)
						self.handleFile(subor,name,root)
						subor.close
		#bol zadany subor
		elif(params.is_dir == False and params.infilec == 1):
			try:
				subor = open(root)
			except IOError:
				sys.stderr.write("Nepodarilo sa otvorit vstupny subor\n")
				sys.exit(2)

			self.handleFile(subor,os.path.basename(root),root)
			subor.close			

		printres.printStats()

###################################################
#Vypise statistiky najdenych elementov
###################################################
class Stats:
	'Vypise zvolene statistiky'

	def printStats(self):
		path_len_max = len("CELKEM:")
		value_len_max = 0
		act_len = 0
		final = ''
		count = 0
		opened = False

		#zoradi cesty
		paths = sorted(parse.mix, key = lambda path: path[0])

		#bol zadany vystupny subor
		if(params.outfilec > 0):
			try:
				subor = open(params.outfile, "w", encoding='ISO-8859-2')
				opened = True
			except IOError:
				sys.stderr.write("Nepodarilo sa otvorit vystupny subor\n")
				sys.exit(3)

		#najde najdlhsiu path a spocita celkem
		for i in range(len(paths)):
			if(len(paths[i][0]) > path_len_max):
				path_len_max = len(paths[i][0])

			count += paths[i][1]

		#sirku praveho stlpca urcuje dlzka retazca celkoveho poctu
		value_len_max = len(str(count))

		#vypise statistiky, zoradene
		for i in range(len(paths)):
			act_path_len = len(paths[i])
			act_val_len = len(str(paths[i][1]))

			if(act_path_len < path_len_max and act_val_len < value_len_max):
				line = paths[i][0].ljust(path_len_max,' ') + ' ' + str(paths[i][1]).rjust(value_len_max,' ') + "\n"
			elif(act_path_len < path_len_max and act_val_len == value_len_max):
				line = paths[i][0].ljust(path_len_max,' ') + ' ' + str(paths[i][1]) + "\n"
			elif(act_path_len == path_len_max and act_val_len < value_len_max):
				line = paths[i][0] + ' ' + str(paths[i][1]).rjust(value_len_max,' ') + "\n"		
			else:
				line = paths[i][0] + ' ' + str(paths[i][1]) + "\n"
			
			if(params.outfilec > 0):
				subor.write(line)
			else:
				sys.stdout.write(line)

		if(params.outfilec > 0):
			final = "CELKEM:"
			subor.write(final.ljust(path_len_max) + ' ' + str(count) + '\n')
		else:
			final = "CELKEM:"
			sys.stdout.write(final.ljust(path_len_max) + ' ' + str(count) + '\n')

		if(opened == True):
			subor.close()


#######################
#Zmaze nepotrebne prvky
#######################
class RemoveNotNeeded:

	'Vymaze nepotrebne elementy zo zdrojoveho textu pre zjednodusenie vyhladavania'

	#zabezpeci nevyhodnocovanie v:
	#	makrach
	#	definiciach konstant
	#	includoch
	def gridElements(self,line):

		#odmazem pripadne medzery na zaciatku a na konci riadku
		tmp = line.strip()
		tmp = line.rstrip()

		if(tmp.startswith("#") and tmp.find("\\") != -1):
			parse.multiline_macro = True	#jedna sa o viacriadkovu definiciu, zapamatam si
			return ""
		elif(tmp.startswith("#") and parse.multiline_macro == False):
			return ""
		elif(parse.multiline_macro == True and tmp.find("\\") != -1):
			return ""
		elif(parse.multiline_macro == True and tmp.find("\\") == -1):
			parse.multiline_macro = False
			return ""

		return tmp

	#zabezpeci nevyhodnocovanie v:
	#	komentaroch
	def comments(self,line):

		tmp = line
		start = -1
		end = -1
		tmp2 = ""

		#jednoriadkovy komentar od zaciatku riadku
		if(tmp.startswith("//")):
			return ""

		#jednoriadkovy komentar za prikazmi, mimo viacriadkoveho komentara
		start = tmp.find("//")

		lit_start = tmp.find('"') #vyhladam "

		#ak sa nasiel znak jednoriadkoveho komentara uchovam si vsetko za nim
		if(start != -1):
			tmp2 = tmp[start+2:]

		lit_end = tmp2.find('"') + len(tmp[:lit_start+1])	#v zvysku vyhladam ukoncovaci znak retazca		

		if(start != -1 and parse.mline_comment == False and lit_start < start and lit_end > start):	#komentar je sucastou retazca, nemazem ho
			return tmp
		elif(start != -1 and parse.mline_comment == False):
			return tmp[:start]

		#viacriadkove komentare
		#	prechadza riadok v cykle, pre pripad ze by bolo viac
		#	komentarov na jednom riadku
		while(1):
			start = tmp.find("/*")
			end = tmp.find("*/")

			lit_start = tmp.find('"') #vyhladam "
			
			#ak sa nasiel uvodny znak literalu uchovam vsetko za nim
			if(lit_start != -1):
				lit_end = tmp[lit_start+1:].find('"') + len(tmp[:lit_start+1])		
		
			#javi sa ako zaciatok viacriadkoveho komentara,
			#ktory pokracuje na dalsich riadkoch, je to vsak iba retazec
			if(start != -1 and end == -1 and (lit_start != -1 and lit_start < start)):
				return tmp
			#vyzera ako viacriadkovy komentar na jednom riadku,
			#je to vsak tiez iba retazec				
			elif(start != -1 and end != -1 and ((lit_start != -1 and lit_start < start) and (lit_end != -1 and lit_end > end))):
				return tmp
			#vyzera ako koniec viacriadkoveho komentara, je to vsak tiez iba retazec				
			elif(start == -1 and end != -1 and (lit_end != -1 and lit_end > end)):
				return tmp
			elif(start != -1 and end == -1):
				parse.mline_comment = True	#komentar este neskoncil
				tmp = tmp[:start]
				return tmp
			elif(start != -1 and end != -1):
				tmp = tmp[:start] + tmp[end+2:]
			elif(start == -1 and end != -1):
				parse.mline_comment = False	#komentar skoncil
				tmp = tmp[end+2:]	#vymaze
			elif(start == -1 and end == -1 and parse.mline_comment == True):
				return ""
			elif(start == -1 and end == -1 and parse.mline_comment == False):
				break

		return tmp

	#zabezpeci nevyhodnocovanie v:
	#	retazcovych literaloch
	def strings(self,line):

		tmp = line
		return (re.sub("(\"\")|(\".*?[^\\\\]\")","",tmp))

	#zabezpeci nevyhodnocovanie v:
	#	znakovych literaloch
	def chars(self,line):

		tmp = line
		return re.sub( "'.*?'", '', tmp)

##########################
#		MAIN 			 #
##########################
if (__name__=="__main__"):
	params = handleParams()
	params.handle()
	remove = RemoveNotNeeded();
	printres = Stats()
	parse = find()
	parse.FindElements(params)

#regexp pre function calls (?!\b(if|while|for)\b)\b\w+(?=\s*\()