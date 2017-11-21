"""
/*****************************************************************************
 * Copyright (c) 2016, Palo Alto Networks. All rights reserved.              *
 *                                                                           *
 * This Software is the property of Palo Alto Networks. The Software and all *
 * accompanying documentation are copyrighted.                               *
 *****************************************************************************/

Copyright 2016 Palo Alto Networks

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import urllib2
import ssl
import xml.etree.ElementTree as et
import datetime
import time
import sys
import json


stackname=""
account=""
ScalingParameter=""
sqs_msg=None

sys.path.append('lib/')
import pan.asglib as lib

tag_key="PANW-NAT-STATUS"

remote=1

if remote > 0:
    import boto3
    cw_client = boto3.client('cloudwatch')
    ec2 = boto3.resource('ec2')
    ec2_client = ec2.meta.client
    lambda_client = boto3.client('lambda')

gwMgmtIp=[]

firewall_cmd = {
                'DataPlaneCPUUtilization': '<show><system><state><filter>sys.monitor.s1.dp0.exports</filter></state></system></show>',
                'SessionUtilization': '<show><system><state><filter>sw.mprelay.s1.dp0.stats.session</filter></state></system></show>'
               }

def pan_print(s):
    if remote > 0:
        logger.info(s)
        return
    print(s)
    return

def runCommand(gcontext, cmd, gwMgmtIp, api_key):
    try:
        response = urllib2.urlopen(cmd, context=gcontext, timeout=5).read()
        #pan_print("[RESPONSE] in send command: {}".format(response))
    except Exception as e:
         logger.error("[RunCommand Response Fail]: {}".format(e))
         pan_print("[RunCommand Response Fail]: {}".format(e))
         return None

    resp_header = et.fromstring(response)

    if resp_header.tag != 'response':
        logger.error("[ERROR]: didn't get a valid response from Firewall command: " + cmd)
        pan_print("[ERROR]: didn't get a valid response from Firewall")
        return None

    if resp_header.attrib['status'] == 'error':
        logger.error("[ERROR]: Got an error for the command: " + cmd)
        pan_print("[ERROR]: Got an error for the command: " + cmd)
        return None

    if resp_header.attrib['status'] == 'success':
        return response

    return None

def DataPlaneCPUUtilization(root, namespace, asg_name):
    logger.info('DataPlaneCPUUtilization');
    logger.info('root[0][1].text: ' + str(root[0].text))
    cpu=""
    d=valueToDict(str(root[0].text), "sys.monitor.s1.dp0.exports:")
    if d is None:
        pan_print('Error happened in DataPlaneCPUUtilization: ' + str(root[0].text))
        return

    cpu=float(d['cpu']['1minavg'])
    pan_print('DataPlaneCPUUtilization in percentage: ' + str(cpu))

    if remote == 0:
        return

    if sqs_msg is not None:
        v=lib.getScalingValue(sqs_msg, ScalingParameter)
        if v is not None:
            print(sqs_msg)
            logger.info('Pushing simulated data to CW: ' + str(v))
            cpu=float(v)
        else:
            logger.info('Starting to Publish metrics in namespace: ' + namespace)
    else:
        logger.info('Starting to Publish metrics in namespace: ' + namespace)

    timestamp = datetime.datetime.utcnow()
    response = cw_client.put_metric_data(
                Namespace=namespace,
                MetricData=[{
                        'MetricName': 'DataPlaneCPUUtilization',
                        'Dimensions':[{
                                'Name': 'AutoScalingGroupName',
                                'Value': asg_name
                            }],
                        'Timestamp': timestamp,
                        'Value': cpu,
                        'Unit': 'Percent'
                    }]
    )

    logger.info("[INFO]: Published GOOD metric for {}".format(gwMgmtIp))
    return

def SessionUtilization(root, namespace, asg_name):
    logger.info('SessionUtilization');
    logger.info('root[0][1].text: ' + str(root[0].text))
    sess=0.0
    d=valueToDict(str(root[0].text), "sw.mprelay.s1.dp0.stats.session:")
    if d is None:
        pan_print('Error happened in SessionUtilization: ' + str(root[0].text))
        return

    sess=float(d['session_util'])
    pan_print('SessionUtilization in percentage: ' + str(sess))

    if remote == 0:
        return

    if sqs_msg is not None:
        v=lib.getScalingValue(sqs_msg, ScalingParameter)
        if v is not None:
            print(sqs_msg)
            logger.info('Pushing simulated data to CW: ' + str(v))
            sess=float(v)
        else:
            logger.info('Starting to Publish metrics in namespace: ' + namespace)
    else:
        logger.info('Starting to Publish metrics in namespace: ' + namespace)

    timestamp = datetime.datetime.utcnow()
    response = cw_client.put_metric_data(
                Namespace=namespace,
                MetricData=[{
                        'MetricName': 'SessionUtilization',
                        'Dimensions':[{
                                'Name': 'AutoScalingGroupName',
                                'Value': asg_name
                            }],
                        'Timestamp': timestamp,
                        'Value': sess,
                        'Unit': 'Percent'
                    }]
    )

    logger.info("[INFO]: Published GOOD metric for {}".format(gwMgmtIp))
    return

cw_func_metrics = { 'DataPlaneCPUUtilization': DataPlaneCPUUtilization,
                        'SessionUtilization': SessionUtilization,


def test():
    pan_print('Local Test Start...........')
    ScalingParameter="DataPlaneCPUUtilization"
    ScalingParameter="ActiveSessions"
    ScalingParameter="DataPlaneBufferUtilization"
    ScalingParameter="SessionUtilization"
    ScalingParameter="GPGatewayUtilization"
    ScalingParameter="DataPlaneBufferUtilization"
    Namespace="panw"
    asg_name="test-asg"
    gwMgmtIp="10.4.20.90"
    untrust="1.1.1.1"
    ilb_ip="2.2.2.2"

    api_key = "LUFRPT14MW5xOEo1R09KVlBZNnpnemh0VHRBOWl6TGM9bXcwM3JHUGVhRlNiY0dCR0srNERUQT09"

    # Need this to by pass invalid certificate issue. Should try to fix this
    gcontext = get_ssl_context()

    if isChassisReady(gcontext, gwMgmtIp, api_key) == False:
        pan_print('Chassis is not ready yet')
        return

    cmd = firewall_cmd[ScalingParameter]
    fw_cmd = "https://"+gwMgmtIp+"/api/?type=op&cmd=" + cmd + "&key="+api_key
    logger.info('[INFO]: Sending API command : %s', fw_cmd)
    try:
        response = urllib2.urlopen(fw_cmd, context=gcontext, timeout=5).read()
        logger.info("[RESPONSE] in send command: {}".format(response))
    except Exception as e:
         logger.error("[ERROR]: Something bad happened when sending command")
         logger.error("[RESPONSE]: {}".format(e))
         return
    else:
        logger.info("[INFO]: Got a response from command urlopen")

    resp_header = et.fromstring(response)

    if resp_header.tag != 'response':
        logger.error("[ERROR]: didn't get a valid response from GW")
        return

    if resp_header.attrib['status'] == 'error':
        logger.error("[ERROR]: Got an error for the command")
        return

    if resp_header.attrib['status'] == 'success':
        #The fw responded with a successful command execution.
        logger.info("[INFO]: Successfully executed command urlopen. Now publish metrics")
        pan_print(response)
        cw_func_metrics[ScalingParameter](resp_header, Namespace, asg_name)
        output.write(response)

if remote == 0:
    test()
