import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export interface MigrationLambdaConstructProps {
    vpc: ec2.IVpc;
    rdsEndpoint: string;
    rdsPort: string;
    rdsSecretArn: string;
    databaseName: string;
    apiLambdaSecurityGroup: ec2.SecurityGroup;
}

export class MigrationLambdaConstruct extends Construct {
    public readonly function: lambda.DockerImageFunction;

    constructor(scope: Construct, id: string, props: MigrationLambdaConstructProps) {
        super(scope, id);

        this.function = new lambda.DockerImageFunction(this, 'MigrationFunction', {
            code: lambda.DockerImageCode.fromImageAsset('../../services/api', {
                file: 'Dockerfile.migrate',
            }),

            functionName: 'apiverse-migrate',
            description: 'APIVerse Database Migration Lambda',

            memorySize: 256,
            timeout: cdk.Duration.minutes(5),

            vpc: props.vpc,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            securityGroups: [props.apiLambdaSecurityGroup],

            environment: {
                RDS_ENDPOINT: props.rdsEndpoint,
                RDS_PORT: props.rdsPort,
                DATABASE_NAME: props.databaseName,
                RDS_SECRET_ARN: props.rdsSecretArn,
                
                REDIS_HOST: 'dummy',
                REDIS_PORT: '6379',
                
                JWT_SECRET_KEY: 'dummy',
                JWT_ALGORITHM: 'HS256',
            },
        });

        this.function.addToRolePolicy(new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
                'secretsmanager:GetSecretValue',
            ],
            resources: [props.rdsSecretArn],
        }));

        cdk.Tags.of(this.function).add('Name', 'ApiVerse-Migration-Lambda');
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
