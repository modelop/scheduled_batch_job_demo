# Scheduled Batch Job Example

To run:
* Build and tag the docker image to match the image name in the yaml manifest.
* Edit the arguments for the Python script in the yaml file.
* Change the Cron to suit your needs in the yaml file.
* Run `kubectl create -f job.yaml`

Example model and test data: https://github.com/modelop/consumer-credit-linear-demo
