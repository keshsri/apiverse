import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export interface RdsConstructProps {
    vpc: ec2.IVpc;
    databaseName?: string;
}

export class RdsConstruct extends Construct {
    public readonly instance: rds.DatabaseInstance;
    public readonly secret: secretsmanager.ISecret;
    public readonly securityGroup: ec2.SecurityGroup;

    constructor(scope: Construct, id: string, props: RdsConstructProps) {
        super(scope, id);

        const databaseName = props.databaseName || 'apiverse';

        this.securityGroup = new ec2.SecurityGroup(this, 'RdsSecurityGroup', {
            vpc: props.vpc,
            description: 'Security group for APIVerse PostgreSQL',
            allowAllOutbound: true,
        });

        const dbCredentials = new secretsmanager.Secret(this, 'DbCredentials', {
            secretName: 'apiverse/db-credentials',
            description: 'APIVerse PostgreSQL database credentials',
            generateSecretString: {
                secretStringTemplate: JSON.stringify({ username: 'apiverse_admin' }),
                generateStringKey: 'password',
                excludePunctuation: true,
                includeSpace: false,
                passwordLength: 32,
            },
        });

        this.secret = dbCredentials;

        this.instance = new rds.DatabaseInstance(this, 'PostgresInstance', {
            engine: rds.DatabaseInstanceEngine.postgres({
                version: rds.PostgresEngineVersion.VER_16_6,
            }),
            instanceType: ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            vpc: props.vpc,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            securityGroups: [this.securityGroup],

            databaseName: databaseName,
            credentials: rds.Credentials.fromSecret(dbCredentials),

            allocatedStorage: 20,
            maxAllocatedStorage: 20,
            storageType: rds.StorageType.GP3,
            storageEncrypted: true,

            backupRetention: cdk.Duration.days(1), 
            deleteAutomatedBackups: true,

            multiAz: false,

            publiclyAccessible: false,
            deletionProtection: false,
            removalPolicy: cdk.RemovalPolicy.DESTROY,
        });

        dbCredentials.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);

        cdk.Tags.of(this.instance).add('Name', "ApiVerse-PostgreSQL");
        cdk.Tags.of(this.instance).add('Project', 'ApiVerse');
    }

    public allowConnectionsFrom(securityGroup: ec2.ISecurityGroup): void {
        this.securityGroup.addIngressRule(
            securityGroup,
            ec2.Port.tcp(5432),
            'Allow PostgreSQL access from Lambda'
        );
    }
}