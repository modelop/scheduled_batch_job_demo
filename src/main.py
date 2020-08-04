import argparse
import json
import requests
import datetime
import subprocess
import time
import sys
import os

model_manager_api = "model-manage/api"
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
def get_most_recent_deployable_model_by_tag(tag, gateway_url):
    url = f"{gateway_url}/{model_manager_api}/deployableModels"
    deployable_models = requests.get(url)\
                                .json()['_embedded']['deployableModels']
    tag_filter = lambda x: tag in x['storedModel']['modelMetaData']['tags']
    tagged_deployable_models = list(filter(tag_filter, deployable_models))

    key = lambda x: datetime.datetime\
                            .fromisoformat(x['createdDate'].rstrip('Z'))
    tagged_deployable_models = sorted(tagged_deployable_models, key=key)
    deployable_model = tagged_deployable_models[-1]
    return deployable_model

def get_uuid(deployable_model):
    sm_id = deployable_model['storedModel']['id']
    return sm_id

def create_job(moc_binary,
               uuid,
               input_file_loc,
               output_file_loc,
               job_type,
               region):
    stdout = subprocess.check_output(
        [moc_binary,
         "job",
         "create",
         job_type,
         uuid,
         input_file_loc,
         output_file_loc,
        f"--region={region}"],

        universal_newlines=True)
    job_id = stdout.strip().split(" ")[-1]
    return job_id

def get_job_status(moc_binary, job_id):
    stdout = subprocess.check_output(
        [moc_binary,
         "job",
         "status",
         job_id],
        universal_newlines=True)
    status = stdout.split("\n")[1].split("\t")[-2].strip()
    print(status)
    return status

def get_s3_file(s3_header, s3_domain, path, filename):
    return f"{s3_header}://{S3_ACCESS_KEY}:{S3_SECRET_KEY}@{s3_domain}/{path}/{filename}"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Job Creator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('moc_binary', help='Path to the moc CLI\
                        binary.')
    parser.add_argument('gateway_url', help='URL which points to\
                        MOC dashboard.')
    parser.add_argument('tag', help='Tag of the model to be used')
    parser.add_argument('s3_domain', help='S3 location')
    parser.add_argument('input_path', help='Path to input data')
    parser.add_argument('input_filename_base', help='Input \
                        Filename stub')
    parser.add_argument('output_filename_base', help='Output \
                        filename stub')
    parser.add_argument('--job_type', default='batchjob', help='Job type to be\
                        run.')
    parser.add_argument('--input_filetype', default='json', help='Input \
                        filetype')
    parser.add_argument('--output_filetype', default='json', help='Output \
                        filetype')
    parser.add_argument('--s3_header', default='http', help='S3 header for \
                        bucket containing data')
    parser.add_argument('--output_path', default='output', help='Path to \
                        output data')
    parser.add_argument('--timeout', default=30, help='Number of seconds before\
                        timeout')
    parser.add_argument('--region', default='default-region', help="S3 region\
                        name.")
    args = parser.parse_args()
    return args

def init_moc_cli(moc_binary, gateway_url):
    subprocess.run([moc_binary, "init", gateway_url])
    pass

def run_job(args):
    gateway_url = args.gateway_url
    minute = datetime.datetime.now().minute
    moc_binary = args.moc_binary
    input_filename = f"{args.input_filename_base}_{minute}.{args.input_filetype}"
    output_filename = f"{args.output_filename_base}_{minute}.{args.output_filetype}"
    print(input_filename)
    print(output_filename)
    input_file = get_s3_file(s3_header=args.s3_header,
                             s3_domain=args.s3_domain,
                             path=args.input_path,
                             filename=input_filename)
    output_file = get_s3_file(s3_header=args.s3_header,
                              s3_domain=args.s3_domain,
                              path=args.output_path,
                              filename=output_filename)

    deployable_model = get_most_recent_deployable_model_by_tag(tag=args.tag,
                                                               gateway_url=gateway_url)

    init_moc_cli(moc_binary, gateway_url)
    model_uuid = get_uuid(deployable_model)
    job_uuid = create_job(moc_binary,
                          model_uuid,
                          input_file,
                          output_file,
                          args.job_type,
                          args.region)

    timeout = datetime.datetime.now() + datetime.timedelta(seconds=args.timeout)
    while True:

        if get_job_status(moc_binary, job_uuid) in ['ERROR', 'COMPLETE']:
            break
        if datetime.datetime.now() >= timeout:
            print("Timeout!")
            break
        time.sleep(3)
    if get_job_status(moc_binary, job_uuid) == 'COMPLETE':
        return 0
    else:
        return 1

if __name__ == '__main__':
    args=parse_args()
    status=run_job(args)
    sys.exit(status)
