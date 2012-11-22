#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os, sys, subprocess, time

cont = 1
out = ""
cout = 0

while cont:
	time.sleep(10)
	
	p = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), 'forumactif-phpbb.py')])
	p.wait()
	cont = p.returncode
	
	if out == p.stdout:
		cout += 1
	else:
		out = p.stdout
		cout = 0
	
	if cout >= 10:
		cont = 0
		print "Le retour du script n'as pas changé lors des dix dernières exécutions."

raw_input("Appuyez sur Entrée pour quitter...")
