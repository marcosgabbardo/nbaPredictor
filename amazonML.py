import base64
import json
import os
import boto3
import datetime
import time
import random


def s3Uploader(cvs_file):
    boto3.setup_default_session(region_name='us-east-1')
    s3 = boto3.resource('s3')
    s3.Object("test.sportbet", cvs_file).put(Body=open('data/'+ cvs_file,'rb'))
    print "upload complete!"

def poll_until_completed(entity_id, entity_type_str):

    ml = boto3.client('machinelearning')

    delay = 2
    while True:

        if entity_type_str == 'ds':
            results = ml.get_data_source(DataSourceId = entity_id, Verbose = True)
        elif entity_type_str == 'ml':
            results = ml.get_ml_model(MLModelId = entity_id, Verbose = True)
        elif entity_type_str == 'ev':
            results = ml.get_evaluation(EvaluationId = entity_id)
        elif entity_type_str == 'bp':
            results = ml.get_batch_prediction(BatchPredictionId = entity_id)

        status = results['Status']
        message = results.get('Message', '')
        now = str(datetime.datetime.now().time())
        print("Object %s is %s (%s) at %s" % (entity_id, status, message, now))
        if status in ['COMPLETED', 'FAILED', 'INVALID']:
            break

        # exponential backoff with jitter
        delay *= random.uniform(1.1, 2.0)
        time.sleep(delay)
    print(results)

def build_model(data_s3_url, now, schema_fn, recipe_fn, name, batch_source, train_percent=85):

    ml = boto3.client('machinelearning')

    (train_ds_id, test_ds_id) = create_data_sources(ml, data_s3_url, schema_fn,train_percent, name, now)

    poll_until_completed(train_ds_id, 'ds')
    poll_until_completed(test_ds_id, 'ds')

    ml_model_id = create_model(ml, train_ds_id, recipe_fn, name, now)

    eval_id = create_evaluation(ml, ml_model_id, test_ds_id, name, now)

    return ml_model_id

def create_data_sources(ml, data_s3_url, schema_fn, train_percent, name, now):
    """Create two data sources.  One with (train_percent)% of the data,
    which will be used for training.  The other one with the remainder of the data,
    which is commonly called the "test set" and will be used to evaluate the quality
    of the ML Model.
    """
    train_ds_id = 'ds-' + base64.b32encode(os.urandom(10))
    spec = {
        "DataLocationS3": data_s3_url,
        "DataRearrangement": json.dumps({
            "splitting": {
                "percentBegin": 0,
                "percentEnd": train_percent
            }
        }),
        "DataSchema": open(schema_fn).read(),
    }
    ml.create_data_source_from_s3(
        DataSourceId=train_ds_id,
        DataSpec=spec,
        DataSourceName=name + " - training split_" + str(now),
        ComputeStatistics=True
    )
    print("Created training data set %s" % train_ds_id)

    test_ds_id = 'ds-' + base64.b32encode(os.urandom(10))
    spec['DataRearrangement'] = json.dumps({
        "splitting": {
            "percentBegin": train_percent,
            "percentEnd": 100
        }
    })
    ml.create_data_source_from_s3(
        DataSourceId=test_ds_id,
        DataSpec=spec,
        DataSourceName=name + " - testing split_" + str(now),
        ComputeStatistics=True
    )
    print("Created test data set %s" % test_ds_id)
    return (train_ds_id, test_ds_id)

def create_model(ml, train_ds_id, recipe_fn, name, now):
    """Creates an ML Model object, which begins the training process.
The quality of the model that the training algorithm produces depends
primarily on the data, but also on the hyper-parameters specified
in the parameters map, and the feature-processing recipe.
    """
    model_id = 'ml-' + base64.b32encode(os.urandom(10))
    ml.create_ml_model(
        MLModelId=model_id,
        MLModelName=name + " model_" + str(now),
        MLModelType="MULTICLASS",
        Parameters={
            # Refer to the "Machine Learning Concepts" documentation
            # for guidelines on tuning your model
            "sgd.maxPasses": "100",
            "sgd.maxMLModelSizeInBytes": "104857600",  # 100 MiB
            "sgd.l2RegularizationAmount": "1e-6",
        },
        Recipe=open(recipe_fn).read(),
        TrainingDataSourceId=train_ds_id
    )
    print("Created ML Model %s" % model_id)
    return model_id

def create_evaluation(ml, model_id, test_ds_id, name, now):
    eval_id = 'ev-' + base64.b32encode(os.urandom(10))
    ml.create_evaluation(
        EvaluationId=eval_id,
        EvaluationName=name + " evaluation_" + str(now),
        MLModelId=model_id,
        EvaluationDataSourceId=test_ds_id
    )
    print("Created Evaluation %s" % eval_id)
    return eval_id

# def create_batch_prediction(ml,name, model_id, now, batch_source):
#
#     batch_id  = 'bp-' + base64.b32encode(os.urandom(10))
#
#     ml.create_batch_prediction(
#         BatchPredictionId=batch_id,
#         BatchPredictionName=name + " batch_" + str(now),
#         MLModelId=model_id,
#         BatchPredictionDataSourceId=batch_source,
#         OutputUri="gabbardo.sportbet"
#     )
#     print("Created batch prediction %s" % batch_id)
#     return batch_id


