#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ApiVerseStack } from '../lib/apiverse-stack';

const app = new cdk.App();

new ApiVerseStack(app, 'ApiVerseStack', {
    env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: 'eu-west-1',
    },
    databaseName: 'apiverse',
});

app.synth();
