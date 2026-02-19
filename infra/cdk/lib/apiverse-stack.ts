import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { VpcConstruct } from './constructs/vpc';
import { RdsConstruct } from './constructs/rds';
import { RedisConstruct } from './constructs/redis';
import { LambdaConstruct } from './constructs/lambda';
import { ApiGatewayConstruct } from './constructs/api-gateway';
import { WebhooksConstruct } from './constructs/webhooks';

export interface ApiVerseStackProps extends cdk.StackProps {
    databaseName?: string;
}

export class ApiVerseStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: ApiVerseStackProps) {
        super(scope, id, props);

        const databaseName = props?.databaseName || 'apiverse';

        const vpcConstruct = new VpcConstruct(this, 'Vpc', {
            maxAzs: 2,
            cidr: '10.0.0.0/16',
        });

        const rdsConstruct = new RdsConstruct(this, 'Rds', {
            vpc: vpcConstruct.vpc,
            databaseName: databaseName,
        });

        const redisConstruct = new RedisConstruct(this, 'Redis', {
            vpc: vpcConstruct.vpc,
        });

        const lambdaConstruct = new LambdaConstruct(this, 'Lambda', {
            vpc: vpcConstruct.vpc,
            rdsEndpoint: rdsConstruct.instance.dbInstanceEndpointAddress,
            rdsPort: rdsConstruct.instance.dbInstanceEndpointPort,
            rdsSecretArn: rdsConstruct.secret.secretArn,
            redisEndpoint: redisConstruct.endpoint,
            redisPort: redisConstruct.port,
            databaseName: databaseName,
        });

        rdsConstruct.allowConnectionsFrom(lambdaConstruct.securityGroup);
        redisConstruct.allowConnectionsFrom(lambdaConstruct.securityGroup);

        const apiGatewayConstruct = new ApiGatewayConstruct(this, 'ApiGateway', {
            lambdaFunction: lambdaConstruct.function,
        });

        const webhooksConstruct = new WebhooksConstruct(this, 'Webhooks', {
            lambdaFunction: lambdaConstruct.function,
        });

        new cdk.CfnOutput(this, 'VpcId', {
            value: vpcConstruct.vpc.vpcId,
            description: 'VPC ID',
            exportName: 'ApiVerseVpcId',
        });

        new cdk.CfnOutput(this, 'RdsEndpoint', {
            value: rdsConstruct.instance.dbInstanceEndpointAddress,
            description: 'RDS PostgreSQL Endpoint',
            exportName: 'ApiVerseRdsEndpoint',
        });

        new cdk.CfnOutput(this, 'RdsSecretArn', {
            value: rdsConstruct.secret.secretArn,
            description: 'RDS Credentials Secret ARN',
            exportName: 'ApiVerseRdsSecretArn',
        });

        new cdk.CfnOutput(this, 'RedisEndpoint', {
            value: redisConstruct.endpoint,
            description: 'Redis ElastiCache Endpoint',
            exportName: 'ApiVerseRedisEndpoint',
        });

        new cdk.CfnOutput(this, 'LambdaFunctionArn', {
            value: lambdaConstruct.getFunctionArn(),
            description: 'Lambda Function ARN',
            exportName: 'ApiVerseLambdaArn',
        });

        new cdk.CfnOutput(this, 'ApiGatewayUrl', {
            value: apiGatewayConstruct.getApiUrl(),
            description: 'API Gateway URL',
            exportName: 'ApiVerseApiUrl',
        });

        new cdk.CfnOutput(this, 'EventBusName', {
            value: webhooksConstruct.getEventBusName(),
            description: 'EventBridge Event Bus Name',
            exportName: 'ApiVerseEventBusName',
        });

        new cdk.CfnOutput(this, 'WebhookQueueUrl', {
            value: webhooksConstruct.getQueueUrl(),
            description: 'Webhook SQS Queue URL',
            exportName: 'ApiVerseWebhookQueueUrl',
        });

        cdk.Tags.of(this).add('Project', 'ApiVerse');
        cdk.Tags.of(this).add('Environment', 'dev');
    }
}
