gen:
	./cp/generate.py

debug:
	./cp/generate.py debug

serve: debug
	cd html && python3 -m http.server
