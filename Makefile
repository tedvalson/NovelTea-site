gen:
	./generate.py

debug:
	./generate.py debug

serve: debug
	cd html && python3 -m http.server
