import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface LambdaConstructProps {
    vpc: ec2.IVpc;
    rdsEndpoint: string;
    rdsPort: string;
    rdsSecretArn: string;
    redisEndpoint: string;
    redisPort: string;
    databaseName: string;
}

export class LambdaConstruct extends Construct {
    public readonly function: lambda.DockerImageFunction;
    public readonly securityGroup: ec2.SecurityGroup;

    constructor(scope: Construct, id: string, props: LambdaConstructProps) {
        super(scope, id);

        this.securityGroup = new ec2.SecurityGroup(this, 'LambdaSecurityGroup', {
            vpc: props.vpc,
            description: 'SecurityGroup for APIVerse Lambda',
            allowAllOutbound: true,
        });

        this.function = new lambda.DockerImageFunction(this, 'FastApiFunction', {
            code: lambda.DockerImageCode.fromImageAsset('../../services/api', {
                file: 'Dockerfile',
            }),

            functionName: 'apiverse-api',
            description: 'APIVerse FastAPI application',

            memorySize: 512,
            timeout: cdk.Duration.seconds(30),

            vpc: props.vpc,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            securityGroups: [this.securityGroup],

            environment: {
                RDS_SECRET_ARN: props.rdsSecretArn,
                RDS_ENDPOINT: props.rdsEndpoint,
                RDS_PORT: props.rdsPort,
                DATABASE_NAME: props.databaseName,

                REDIS_HOST: props.redisEndpoint,
                REDIS_PORT: props.redisPort,

                APP_NAME: 'APIVerse',
                DEBUG: 'false',

                JWT_SECRET_KEY: 'changeit',
                JWT_ALGORITHM: 'HS256',
            },

            logRetention: logs.RetentionDays.ONE_WEEK,
            retryAttempts: 0,
        });

        this.function.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'secretsmanager:GetSecretValue',
            ],
            resources: [props.rdsSecretArn],
        }));

        this.function.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'events:PutEvents',
            ],
            resources: ['*'],
        }));

        this.function.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'sqs:SendMessage',
                'sqs:GetQueueUrl',
            ],
            resources: ['*'],
        }));

        cdk.Tags.of(this.function).add('Name', 'ApiVerse-Lambda');
        cdk.Tags.of(this.function).add('Project', 'ApiVerse');

        this.function.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
    }

    public getFunctionArn(): string {
        return this.function.functionArn;
    }

    public getFunctionName(): string {
        return this.function.functionName;
    }
}