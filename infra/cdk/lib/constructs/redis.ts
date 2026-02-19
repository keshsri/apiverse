import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import { Construct } from 'constructs';

export interface RedisConstructProps {
    vpc: ec2.IVpc;
}

export class RedisConstruct extends Construct {
    public readonly cluster: elasticache.CfnCacheCluster;
    public readonly securityGroup: ec2.SecurityGroup;
    public readonly endpoint: string;
    public readonly port: string;

    constructor(scope: Construct, id: string, props: RedisConstructProps) {
        super(scope, id);

        this.securityGroup = new ec2.SecurityGroup(this, 'RedisSecurityGroup', {
            vpc: props.vpc,
            description: 'Security group for APIVerse Redis ElastiCache',
            allowAllOutbound: true,
        });

        const subnetGroup = new elasticache.CfnSubnetGroup(this, 'RedisSubnetGroup', {
            description: 'Subnet group for APIVerse Redis',
            subnetIds: props.vpc.privateSubnets.map(subnet => subnet.subnetId),
            cacheSubnetGroupName: 'apiverse-redis-subnet-group',
        });

        this.cluster = new elasticache.CfnCacheCluster(this, 'RedisCluster', {
            cacheNodeType: 'cache.t3.micro',
            engine: 'redis',
            engineVersion: '7.1',
            numCacheNodes: 1,

            cacheSubnetGroupName: subnetGroup.cacheSubnetGroupName,
            vpcSecurityGroupIds: [this.securityGroup.securityGroupId],

            clusterName: 'apiverse-redis',
            port: 6379,

            snapshotRetentionLimit: 5,
            snapshotWindow: '03:00-05:00',

            preferredMaintenanceWindow: 'sun:05:00-sun:06:00',
            autoMinorVersionUpgrade: true,
        });

        this.cluster.addDependency(subnetGroup);

        this.endpoint = this.cluster.attrRedisEndpointAddress;
        this.port = this.cluster.attrRedisEndpointPort;

        this.cluster.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);
        subnetGroup.applyRemovalPolicy(cdk.RemovalPolicy.DESTROY);

        cdk.Tags.of(this.cluster).add('Name', 'ApiVerse-Redis');
        cdk.Tags.of(this.cluster).add('Project', 'ApiVerse');
    }

    public allowConnectionsFrom(securityGroup: ec2.ISecurityGroup): void {
        this.securityGroup.addIngressRule(
            securityGroup,
            ec2.Port.tcp(6379),
            'Allow Redis access from Lambda'
        );
    }

    public getConnectionString(): string {
        return `redis://${this.endpoint}:${this.port}`;
    }
}