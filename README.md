# Scheduled Batch Job

Dockerfile - You'll have to build a container in which the job can be scheduled by Kubernetes.

1. `docker built -t <some-tag> .` from the directory in which you have the Dockerfile. You'll need the requirements.txt file in the same directory.  The tag needs to be of the form: repo/name:version. 

job.yaml - This will require some modifications depending on how things are configured on your end.
1. You'll need to set the image: field to whatever tag you used in the `docker build` step. 
2. You may want to change the cron. This is set to run once a minute seeing as how this is a demo.
3. You may have to edit the arguments for the Python script. 
* The moc-binary CLI location is set in the Dockerfile, so that should be OK.
* The Gateway URL is the URL you put in your browser to point at the ModelOp Center dashboard. 
* "tag" is an identifier for both your model and the runtime you're using. 
* The next two fields are to set your S3 location information. Note that you just need the domain name and the path. For instance "minio:9000" and "modelop/samples". It defaults to using `http` and it handles the secrets through environment variables. All of this is configurable. 
* The last two required fields are prefixes for input and output files. For example the input prefix should be set to "sample_data" in the example.
* There are also a number of optional flags that you can set for your particular use-case.
src/main.py - This is a Python script which utilizes the moc CLI in order to create a batchjob. It's hard-coded to pick up the current minute M and then pick up the indexed `input_file_prefix`_M.json sitting in S3 and then write it to a file called `output_file_prefix`_M.json in a different location in S3. In your case, you can index by the date or perhaps just not index the files at all and just pick up whatever is in the location and require some data pipeline to handle updating the file in that location. This is Python. You can do anything.

samples/ - just 60 sample data files that run utilizing this model: https://github.com/modelop/consumer-credit-linear-demo

requirements.txt - Any Python libraries you'll need available in your Docker container.

To run:Tag your model with the unique tag of your choice and click "Submit Model." (Clicking "Submit Model" creates a "deployable model" which is a snapshot of the model with all of its artifacts. It's how we version models.)Tag your Runtime with the same unique tag as your model.Run `kubectl create -f job.yaml` to create the cron job.If you need to delete the cron job for whatever reason, just run `kubectl delete cronjob job-runner` (or whatever you set the job name to in the name metadata field in job.yaml)

Note here that the choice of Kubernetes to handle the cron job is a bit arbitrary. You can have Airflow or whatever scheduler you'd like to have run the Python script to create the job. The MLC process and tags will handle it from there.
