init:
	pip install -r requirements.txt
	pip install -e .

test:
	py.test

clean:
	find . -name "*.pyc" -exec rm -rf {} \;

publish:
	python setup.py register
	python setup.py sdist upload
	python setup.py bdist_wheel upload
