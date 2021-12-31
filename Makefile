gen:
	./generate.py

serve: gen
	cd html && python3 -m http.server
