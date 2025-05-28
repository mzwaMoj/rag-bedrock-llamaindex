# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Shows how to generate an embedding with the Amazon Titan Embeddings G1 - Text model (on demand).
"""

import json
import logging
import boto3
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_embedding(model_id, body):
    """
    Generate an embedding with the vector representation of a text input using Amazon Titan Embeddings G1 - Text on demand.
    Args:
        model_id (str): The model ID to use.
        body (str) : The request body to use.
    Returns:
        response (JSON): The embedding created by the model and the number of input tokens.
    """

    logger.info("Generating an embedding with Amazon Titan Embeddings G1 - Text model %s", model_id)

    bedrock = boto3.client(service_name='bedrock-runtime',
                           region_name=os.environ.get('aws_region'),
                           aws_access_key_id=os.environ.get('aws_access_key_id'),
                           aws_secret_access_key=os.environ.get('aws_secret_access_key'))

    accept = "application/json"
    content_type = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=model_id, accept=accept, contentType=content_type
    )

    response_body = json.loads(response.get('body').read())

    return response_body


def main():
    """
    Entrypoint for Amazon Titan Embeddings G1 - Text example.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s: %(message)s")

    model_id = "amazon.titan-embed-text-v1"
    input_text = "What are the different services that you offer?"


    # Create request body.
    body = json.dumps({
        "inputText": input_text,
    })


    try:

        response = generate_embedding(model_id, body)

        print(f"Generated an embedding: {response['embedding']}")
        print(f"Input Token count:  {response['inputTextTokenCount']}")

    except ClientError as err:
        message = err.response["Error"]["Message"]
        logger.error("A client error occurred: %s", message)
        print("A client error occured: " +
              format(message))

    else:
        print(f"Finished generating an embedding with Amazon Titan Embeddings G1 - Text model {model_id}.")


if __name__ == "__main__":
    main()
