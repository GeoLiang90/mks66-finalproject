still: still.mdl lex.py main.py matrix.py mdl.py display.py draw.py gmath.py yacc.py
	python main.py still.mdl

anim:
	python main.py test.mdl

hall:
	python main.py hallway.mdl

clean:
	rm *pyc *out parsetab.py

clear:
	rm *pyc *out parsetab.py *ppm
