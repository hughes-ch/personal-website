[![hughes-ch](https://circleci.com/gh/hughes-ch/personal-website.svg?style=shield)](https://app.circleci.com/pipelines/github/hughes-ch/personal-website)
[![Netlify Status](https://api.netlify.com/api/v1/badges/c420dc8f-2881-403b-8479-6718169fdb56/deploy-status)](https://app.netlify.com/sites/zen-engelbart-f16ad6/deploys)

# My Blog and Online Resume
This is the code repository for Chris Hughes' blog and online resume, developed with Python 3.8 and Flask 2.0.1.

[Want to see it live?](https://blog.chrishughesdev.com) 

## Installation
The easiest way to install onto a local machine is just by pulling from github. Next, create a virtual environment
with:

     python -m venv <name_of_env>
  
This project uses pip for dependency management. To install dependencies, type:

    pip install -r requirements.txt
  
## Testing 
This project uses nosetest for unit testing. Use these two commands when running unit tests:
 
    export CONFIG_SPEC_INI='development.ini'
    nosetests -sv --with-coverage --cover-erase --cover-package=src --cover-xml
  
The first command sets the CONFIG_SPEC_INI to use the development configuration. The biggest benefit to this is 
that any external sources are not loaded. This allows unit tests to run without ping'ing online resources. 
  
The second command runs the unit tests and stores the results in coverage.xml.
  
To start the site on the local machine, use these commands:
  
    export FLASK_APP=src
    export FLASK_ENV='development'
    export CONFIG_SPEC_INI='development.ini'
    flask run --host 0.0.0.0
  
Then you can type "localhost:5000" into your browser search bar and the website will be rendered. Any machine on
the local network will also be able to reach the website using your machine's IP and port 5000. This can be useful
to test mobile.
  
This site uses Frozen-Flask on deployment. The Frozen-Flask module renders pseudo-dynamic Flask applications (ones
that don't change between deploys, like this one) as static HTML files. The major benefit is that the website can 
be served much quicker and hosted on cheaper services. The main drawback is that it has another thing to test...
  
To test the static website rendering, first build the static website:
  
    export FLASK_APP='src'
    export FLASK_ENV='production'
    export CONFIG_SPEC_INI='development.ini'
    flask build

Then, render the static website locally:
  
    export FLASK_APP='src'
    export FLASK_ENV='production'
    export CONFIG_SPEC_INI='development.ini'
    flask run-static 0.0.0.0

Make sure everything in newly added features was built correctly by Frozen-Flask before deploying. 
  
If a fully deploy-ready version of the website (including online services) is desired, use these commands:
  
    export FLASK_APP='src'
    flask build
    flask run-static 0.0.0.0
  
I find it useful to put each of the above sets of commands in the virtual environment /bin directory.
    
## Deploying
This site is hosted on Netlify. To deploy, simply submit a pull request for the main branch. Once 
the pull request is completed, Netlify will convert the Flask app into static HTML and deploy.
  
## Workflow
There are two permanent branches in this git repository:
1. main - Code on this branch is to be deployed immediately. Changes must be submitted via pull request
2. dev - Code ready to be deployed. Code changes can be merged directly from work branches

Any other changes should be made on temporary work branches. Example for a new "feature-1":
  
    main
    |----dev
    |    |----feature-1
    |    |    | commit f0390e2
    |    |<---| git merge
    |<---|      Pull request on github
  
CircleCI is currently used as the main CI tool. When a pull request is submitted to main, CircleCi runs
unit tests. Netlify also creates a deploy preview. Once both of these tests pass, the change can be 
pulled to main. 
  
Once code has been pulled to main, it is deployed by Netlify and becomes live. 

