import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export interface ApiGatewayConstructProps {
    lambdaFunction: lambda.IFunction;
    domainName?: string;
}

export class ApiGatewayConstruct extends Construct {
    public readonly api: apigateway.RestApi;
    public readonly deployment: apigateway.Deployment;

    constructor(scope: Construct, id: string, props: ApiGatewayConstructProps) {
        super(scope, id);

        this.api = new apigateway.RestApi(this, 'ApiVerseApi', {
            restApiName: 'apiverse-api',
            description: 'APIVerse API Management Platform',

            deploy: true,
            deployOptions: {
                stageName: 'dev',
                loggingLevel: apigateway.MethodLoggingLevel.INFO,
                dataTraceEnabled: true,
                metricsEnabled: true,

                throttlingRateLimit: 100,
                throttlingBurstLimit: 200,
            },

            defaultCorsPreflightOptions: {
                allowOrigins: apigateway.Cors.ALL_ORIGINS,
                allowMethods: apigateway.Cors.ALL_METHODS,
                allowHeaders: [
                    'Content-Type',
                    'Authorization',
                    'X-Api-Key',
                ],
            },

            cloudWatchRole: true,
            endpointTypes: [apigateway.EndpointType.REGIONAL],
        });
        const lambdaIntegration = new apigateway.LambdaIntegration(props.lambdaFunction, {
            proxy: true, 
            allowTestInvoke: true,
        });

        this.api.root.addMethod('ANY', lambdaIntegration);

        this.api.root.addProxy({
            defaultIntegration: lambdaIntegration,
            anyMethod: true, 
        });

        const logGroup = new logs.LogGroup(this, 'ApiGatewayAccessLogs', {
            logGroupName: `/aws/apigateway/apiverse`,
            retention: logs.RetentionDays.ONE_WEEK,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        const stage = this.api.deploymentStage;
        stage.node.addDependency(logGroup);

        cdk.Tags.of(this.api).add('Name', 'ApiVerse-API-Gateway');
        cdk.Tags.of(this.api).add('Project', 'ApiVerse');
    }

    public getApiUrl(): string {
        return this.api.url;
    }

    public getApiId(): string {
        return this.api.restApiId;
    }
}